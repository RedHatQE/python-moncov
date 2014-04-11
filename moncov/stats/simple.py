import ast
import moncov
import collections
from rate import Rate

class Visitor(ast.NodeVisitor):
    def __init__(self, hit_count={}):
        self.hit_count = hit_count
        self.lines = set()
        self.line_rate = None
        self.branch_rate = None

    def add_line(self, node):
        '''ad node and update self.line_rate'''
        if not hasattr(node, 'lineno') or node.lineno in self.lines:
            # already encountered --- skip
            return
        self.lines.add(node.lineno)
        if node.lineno in self.hit_count:
            # this line was executed
            rate = Rate(1, 1)
        else:
            rate = Rate(0, 1)
        if self.line_rate is None:
            # initial state
            self.line_rate = rate
        else:
            self.line_rate |= rate

    def add_branch(self, node):
        '''add a branched node and update self.branch_rate'''
        orelse_hits = set([subnode.lineno for subnode in node.orelse if
                            hasattr(subnode, 'lineno') and subnode.lineno in self.hit_count])
        body_hits = set([subnode.lineno for subnode in node.body if
                            hasattr(subnode, 'lineno') and subnode.lineno in self.hit_count])
        if node.orelse:
            # node has both orelse and body branch

            if orelse_hits and body_hits:
                # 2 branches and 2 hits
                rate = Rate(2, 2)
            else:
                # either orelse or body without hits
                rate = Rate(1, 2)
        else:
            # just body branch
            if body_hits:
                # body was executed
                rate = Rate(1, 1)
            else:
                rate = Rate(0, 1)
        if self.branch_rate is None:
            # initial state
            self.branch_rate = rate
        else:
            self.branch_rate |= rate


    def visit_If(self, node):
        '''visit all If-sub nodes and update branch rate'''
        self.visit(node.test)
        for subnode in node.body + node.orelse:
            self.visit(subnode)
        self.add_branch(node)

    def visit_While(self, node):
        self.visit(node.test)
        for subnode in node.body + node.orelse:
            self.visit(subnode)
        self.add_branch(node)

    def visit_For(self, node):
        self.visit(node.target)
        self.visit(node.iter)
        for subnode in node.body + node.orelse:
            self.visit(subnode)
        self.add_branch(node)

    def generic_visit(self, node):
        self.add_line(node)
        super(Visitor, self).generic_visit(node)


FileStatus = collections.namedtuple('FileStatus', ['filename',
                'branch_rate', 'line_rate'])
FileErrorStatus = collections.namedtuple('FileErrorStatus', ['filename', 'error'])

def get_stats(db=None, whitelist=None, blacklist=None):
    if db is None:
        db = moncov.conf.get_db()
    whitelist = moncov.conf.get_whitelist(whitelist)
    blacklist = moncov.conf.get_blacklist(blacklist)
    cursor_grouped = db.lines.aggregate([{"$group": {"_id": "$_id.file",
        "lines": {"$addToSet": {"line": "$_id.line", "value": "$value"}}}}])
    stats = []
    for doc in cursor_grouped['result']:

        filename = doc['_id']

        if not filename:
            # happens when the db is broken
            stats.append(FileErrorStatus(filename=filename, error=ValueError('no-filename')))
            continue
        if not any([pattern.match(filename) for pattern in whitelist]) or \
            any([pattern.match(filename) for pattern in blacklist]):
            stats.append(FileErrorStatus(filename=filename, error=ValueError('filtered-away')))
            continue
        try:
            with open(filename) as fd:
                src = fd.read()
        except Exception as e:
            stats.append(FileErrorStatus(filename=filename, error=e))
            continue
        try:
            tree = ast.parse(src)
        except Exception as e:
            stats.append(FileErrorStatus(filename=filename, error=e))
            continue
        visitor = Visitor(hit_count=dict([(int(pair['line']),
            int(pair['value'])) for pair in doc['lines']]))
        visitor.visit(tree)

        stats.append(FileStatus(filename=filename, line_rate=visitor.line_rate,
                branch_rate=visitor.branch_rate))

    return stats

def print_stats(db=None, whitelist=None, blacklist=None):
    stats = get_stats(db=db, whitelist=whitelist, blacklist=blacklist)
    print "# filename, linerate, branchrate"
    for file_status in stats:
        if isinstance(file_status, FileStatus):
            if file_status.branch_rate is not None:
                branch_rate = '%1.2f' % file_status.branch_rate
            else:
                branch_rate = 'N/A'
            if file_status.line_rate is not None:
                line_rate = '%1.2f' % file_status.line_rate
            else:
                line_rate = 'N/A'
            print  file_status.filename + ', ' + line_rate + ', ' + branch_rate
        elif isinstance(file_status, FileErrorStatus):
            print "# %s: %r" % (file_status.filename, file_status.error)
        else:
            print "# bad file_status: %r" % file_status

if __name__ == '__main__':
    print_stats()
