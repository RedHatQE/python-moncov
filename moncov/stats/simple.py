# prevent tracing ourselves
import moncov
import ast
import sys
import fractions

class Rate(fractions.Fraction):
    def __or__(self, other):
        '''grow the ratio and the pie size'''
        return type(self)(self.numerator + other.numerator,
                        self.denominator + other.denominator)

class Status(object):
    def __init__(self, lineno=0, lines=set(), hits=set(), line_rate=Rate(1,1),
            branch_rate=Rate(1, 1)):
        self.lineno = lineno
        self.lines = lines
        self.line_rate = line_rate
        self.branch_rate = branch_rate
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
        self.branch_rate = self.branch_rate | other.branch_rate
        self.line_rate = self.line_rate | other.line_rate

    def __repr__(self):
        return '%r(%r, lines=%r, hits=%r, line_rate=%r, branch_rate=%r)' % (
                type(self), self.lineno, self.lines, self.hits, self.line_rate,
                self.branch_rate)

class Visitor(ast.NodeVisitor):
    def __init__(self, hit_count={}):
        # hit_count is a mapping: lineno->line_hits
        self.hit_count = hit_count
        # set of lines explored during parsing
        self.lines = set()
        # all hit/executed lines
        self.hits = set(self.hit_count.keys())
        self.stack = [Status(lineno=0, hits=self.hits)]
        super(Visitor, self).__init__()

    def visit_If(self, node):
        # need to distinguish between test/body/orelse if statement subtrees
        # the default branch rate of an if/test statement is 1/2
        self.stack.append(Status(node.lineno, lines=self.lines,
            hits=self.hits, branch_rate=Rate(1, 2)))
        self.visit(node.test)
        for sub_node in node.body:
            self.visit(sub_node)
        for sub_node in node.orelse:
            self.visit(sub_node)
        current = self.stack.pop()
        if node.lineno in self.hit_count and \
                self.hit_count[node.lineno] > max([self.hit_count[line] for line in
                current.lines if line in self.hit_count]):
            # there were some executions with negative test outcome
            # thus the branch_rate is 2 of 2 i.e. 1/1
            currnent.branch_rate = Rate(1, 1)
        self.top.merge(current)

    #visit_IfExp = visit_If

    def generic_visit(self, node):
        # update top status node
        if hasattr(node, 'lineno'):
            # a line-node
            self.top.lines.add(node.lineno)
            if node.lineno in self.hits:
                # executed line
                self.top.line_rate |= Rate(1, 1)
            else:
                self.top.line_rate |= Rate(0, 1)
        super(Visitor, self).generic_visit(node)

    @property
    def top(self):
        return self.stack[-1]

    @top.setter
    def top(self, value):
        self.stack[-1] = value



def print_stats(db=None, whitelist=None, blacklist=None):
    if db is None:
        db = moncov.conf.get_db()
    whitelist = moncov.conf.get_whitelist(whitelist)
    blacklist = moncov.conf.get_blacklist(blacklist)
    cursor_grouped = db.lines.aggregate([{"$group": {"_id": "$_id.file",
        "lines": {"$addToSet": {"line": "$_id.line", "value":  "$value"}}}}])
    print "# filename: linerate, branchrate"
    for doc in cursor_grouped['result']:
        filename = doc['_id']
        if not any([pattern.match(filename) for pattern in whitelist]) or \
            any([pattern.match(filename) for pattern in blacklist]):
            continue
        print "%s" % filename,
        if str(filename).startswith('<'):
            print "...not a *.py file"
            continue
        try:
            with open(filename) as fd:
                src = fd.read()
        except Exception as e:
            print "...can't read file: %r" % e
            continue
        try:
            tree = ast.parse(src)
        except Exception as e:
            print "...has syntax errors: %r" % e
            continue
        visitor = Visitor(hit_count=dict([(int(pair['line']),
            int(pair['value'])) for pair in doc['lines']]))
        visitor.visit(tree)
        print ": %1.2f, %1.2f" % \
                (visitor.top.line_rate, visitor.top.branch_rate)

if __name__ == '__main__':
    print_stats()
