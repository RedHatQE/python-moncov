# prevent tracing ourselves
import moncov
import ast
import sys
import fractions
from fractions import Fraction
import collections


class Status(object):
    def __init__(self, lineno=0, lines=set(), hits=set(), branch_rate=None):
        self.lineno = lineno
        self.lines = lines
        self.branch_rate = branch_rate or [0, 0]
        self.hits = hits

    @property
    def lines(self):
        return self._lines

    @lines.setter
    def lines(self, other_set):
        # ensure self.lineno is kept in the set
        self._lines = other_set | set([self.lineno])

    def merge(self, other):
        # merge statuses <<=
        assert type(self) is type(other)
        self.lines |= other.lines
        self.hits |= other.hits
        self.branch_rate = [self.branch_rate[0] + other.branch_rate[0], self.branch_rate[1] + other.branch_rate[1]]
        

    def __repr__(self):
        return '%r(%r, lines=%r, hits=%r, branch_rate=%r)' % (
                type(self), self.lineno, self.lines, self.hits, self.branch_rate)

class Visitor(ast.NodeVisitor):

    def __init__(self, hit_count={}, branch_rate=None):
        # hit_count is a mapping: lineno->line_hits
        self.hit_count = hit_count
        # set of lines explored during parsing
        self.lines = set()
        # all hit/executed lines
        self.hits = set(self.hit_count.keys())
        self.branch_rate = branch_rate or [0,0]
        self.stack = [Status(lineno=0, hits=self.hits, branch_rate=self.branch_rate)]
        super(Visitor, self).__init__()

    def visit_If(self, node):
        # need to distinguish between test/body/orelse if statement subtrees
        # the default branch rate of an if/test statement is 1/2
        self.stack.append(Status(node.lineno, lines=self.lines,
            hits=self.hits, branch_rate=self.branch_rate))
            
        self.visit(node.test)
        for sub_node in node.body:
            self.visit(sub_node)
        for sub_node in node.orelse:
            self.visit(sub_node)
        current = self.stack.pop()
        
        
        if node.lineno in self.hit_count:
                
            hits = set([self.hit_count[line] for line in
            current.lines-set([node.lineno]) if line in self.hit_count])
            if hits and (self.hit_count[node.lineno] > max(hits)):
                self.branch_rate = [self.branch_rate[0]+2, self.branch_rate[1]+2]

            else:
                self.branch_rate = [self.branch_rate[0]+1, self.branch_rate[1]+2]
      
        current.branch_rate = self.branch_rate
        self.top.merge(current)

    #visit_IfExp = visit_If

    def generic_visit(self, node):
        # update top status node
        if hasattr(node, 'lineno'):
            # a line-node
            self.top.lines.add(node.lineno)

        super(Visitor, self).generic_visit(node)

    @property
    def top(self):
        return self.stack[-1]

    @top.setter
    def top(self, value):
        self.stack[-1] = value


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

        if visitor.branch_rate[1] != 0:
            branch_rate = float(visitor.branch_rate[0])/visitor.branch_rate[1]
        else:
            branch_rate = 0
    
        stats.append(FileStatus(filename=filename, line_rate=float(len(doc['lines']))/(len(visitor.top.lines)-1), branch_rate=branch_rate))

    return stats

def print_stats(db=None, whitelist=None, blacklist=None):
    stats = get_stats(db=db, whitelist=whitelist, blacklist=blacklist)
    print "# filename, linerate, branchrate"
    for file_status in stats:
        if isinstance(file_status, FileStatus):
            print "%s: %1.2f, %1.2f" % (file_status.filename, file_status.line_rate,
                    file_status.branch_rate)
        elif isinstance(file_status, FileErrorStatus):
            print "# %s: %r" % (file_status.filename, file_status.error)
        else:
            print "# bad file_status: %r" % file_status

if __name__ == '__main__':
    print_stats()
