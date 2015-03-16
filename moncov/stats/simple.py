import ast
import moncov
import collections
import os
from rate import Rate

class Visitor(ast.NodeVisitor):
    def __init__(self, hit_count={}):
        self.hit_count = hit_count
        self.lines = set()
        self.branches = set()
        self.conditions = {}
        self.line_rate = None
        self.branch_rate = None

    def add_line(self, node):
        '''ad node and update self.line_rate return True if line was added'''
        if not hasattr(node, 'lineno') or node.lineno in self.lines:
            # already encountered --- skip
            return False
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
        return True

    def get_condition_rate(self, node):
        '''figure out current node's condition rate/coverate'''
        orelse_hits = set([subnode.lineno for subnode in node.orelse if
                            hasattr(subnode, 'lineno') and subnode.lineno in self.hit_count])
        body_hits = set([subnode.lineno for subnode in node.body if
                            hasattr(subnode, 'lineno') and subnode.lineno in self.hit_count])
        if node.orelse:
            # node has both orelse and body branch

            if orelse_hits and body_hits:
                # 2 branches and 2 hits
                rate = Rate(2, 2)
            elif orelse_hits or body_hits:
                # either orelse or body without hits
                rate = Rate(1, 2)
            else:
                # no hits at all
                rate = Rate(0, 2)
        else:
            # just body branch
            if body_hits:
                # body was executed
                rate = Rate(1, 1)
            else:
                rate = Rate(0, 1)
        return rate

    def get_branch_rate(self, node):
        '''figure out current node's branch rate'''
        rate = self.get_condition_rate(node)
        for subnode in node.body + node.orelse:
            sub_rate = self.visit(subnode)
            if sub_rate is not None:
                sub_rate |= rate
        return rate


    def add_branch(self, node):
        '''add a branched node and update self.branch_rate'''
        branch_rate = self.get_branch_rate(node)
        if self.branch_rate is None:
            # initial state
            self.branch_rate = branch_rate
        else:
            self.branch_rate |= branch_rate
        self.branches.add(node.lineno)
        self.conditions[node.lineno] = self.get_condition_rate(node)

    def visit_If(self, node):
        '''visit all If-sub nodes and update branch rate'''
        self.add_line(node)
        self.visit(node.test)
        return self.add_branch(node)

    def visit_While(self, node):
        self.add_line(node)
        self.visit(node.test)
        return self.add_branch(node)

    def visit_For(self, node):
        self.add_line(node)
        self.visit(node.target)
        self.visit(node.iter)
        return self.add_branch(node)

    def generic_visit(self, node):
        self.add_line(node)
        return super(Visitor, self).generic_visit(node)


FileStatus = collections.namedtuple('FileStatus', ['filename',
                'branch_rate', 'line_rate', 'branches', 'lines', 'conditions', 'hit_count'])
FileErrorStatus = collections.namedtuple('FileErrorStatus', ['filename', 'error'])

def get_stats(db=None, whitelist=None, blacklist=None):
    if db is None:
        db = moncov.conf.get_db()
    whitelist = moncov.conf.get_whitelist(whitelist)
    blacklist = moncov.conf.get_blacklist(blacklist)

    stats = []

    for filename in moncov.data.filenames(db):
        # does the filename require processing?
        if not any([pattern.match(filename) for pattern in whitelist]) or \
            any([pattern.match(filename) for pattern in blacklist]):
            stats.append(FileErrorStatus(filename=filename, error=ValueError('filtered-away')))
            continue
        # fetch the filename content
        try:
            with open(filename) as fd:
                src = fd.read()
        except Exception as e:
            # error reading filename --- mark an error status
            stats.append(FileErrorStatus(filename=filename, error=e))
            continue
        # parse source filename content
        try:
            tree = ast.parse(src)
        except Exception as e:
            # not valid python code --- could happen because file changed
            # between being traced and processed here
            stats.append(FileErrorStatus(filename=filename, error=e))
            continue
        # fetch lineno--hitcount stats
	hit_count = dict()
        for arc in moncov.data.filename_arcs(db, filename):
            hit_count[moncov.data.arc2line(arc)] = moncov.data.filename_arc_hits(db, filename, arc)

        # calculate the source file AST rates
        visitor = Visitor(hit_count=hit_count)
        visitor.visit(tree)
        # record the source filename stats
        stats.append(FileStatus(filename=filename, line_rate=visitor.line_rate,
                branch_rate=visitor.branch_rate, lines=visitor.lines, branches=visitor.branches,
                hit_count=visitor.hit_count, conditions=visitor.conditions))

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

def get_stats_xml(db=None, whitelist=None, blacklist=None):
        '''return a header-only cobertura xml'''
        stats = get_stats(db=db, whitelist=whitelist, blacklist=blacklist)
        # calculate overall rates
        good_stats = [result for result in stats if type(result) is FileStatus]
        branch_rates = [result.branch_rate for result in good_stats
                            if type(result.branch_rate) is Rate]
        line_rates = [result.line_rate for result in good_stats
                            if type(result.line_rate) is Rate]
        line_rate = None
        if line_rates:
            line_rate = reduce(lambda result, rate: result | rate,
                                    line_rates[1:], line_rates[0])
        branch_rate = None
        if branch_rates:
            branch_rate = reduce(lambda result, rate: result | rate,
                                    branch_rates[1:], branch_rates[0])
        # create module xml nodes
        import time
        import lxml.etree as ET
        from lxml.builder import E
        packages = []
        for result in good_stats:
            line_elements = []
            for line in result.lines:
                line_element = E.line(number=str(line), hits=line in result.hit_count and \
                                    str(result.hit_count[line]) or "0")
                if line in result.branches:
                    line_element.set('branch', 'true')
                    line_element.set('condition-coverage', "{0:}% ({1:})".format(
                                        int(result.conditions[line]*100), result.conditions[line]))
                line_elements.append(line_element)
            class_element = E("class", E.methods(), E.lines(*line_elements), name=os.path.basename(result.filename),
                                complexity='0.00', filename=result.filename)
            class_element.set('branch-rate', "%1.4f" % (result.branch_rate or 0.0))
            class_element.set('line-rate', "%1.4f" % (result.line_rate or 0.0))
            package = E.package(E.classes(class_element), name="", complexity='0.00')
            package.set('branch-rate', "%1.4f" % (result.branch_rate or 0.0))
            package.set('line-rate', "%1.4f" % (result.line_rate or 0.0))
            packages.append(package)
        tree = E.coverage(
            E.packages(*packages),
            timestamp=str(int(time.time()*1000)),
            version='3.7',
            complexity='0.00'
        )
        tree.set('branch-rate', '%1.4f' % (branch_rate or 0.0))
        tree.set('line-rate', '%1.4f' % (line_rate or 0.0))
        tree.set('lines-covered', line_rate and str(line_rate.numerator) or "0")
        tree.set('lines-valid', line_rate and str(line_rate.denominator) or "0")
        tree.set('branches-covered', branch_rate and str(branch_rate.numerator) or "0")
        tree.set('branches-valid', branch_rate and str(branch_rate.denominator) or "0")
        return ET.tostring(tree, pretty_print=True, xml_declaration=True,
                            doctype="<!DOCTYPE coverage SYSTEM 'http://cobertura.sourceforge.net/xml/coverage-04.dtd'>")



if __name__ == '__main__':
    #print_stats()
    print get_stats_xml()
