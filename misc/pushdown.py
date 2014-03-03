#!/usr/bin/pytho
import ast
import collections
import sys

# *_[EX] events: Enter eXit
M_E = 'M_E' # Module
M_X = 'M_X'
F_E = 'F_E' # Function
F_X = 'F_X'
C_E = 'C_E' # Class
C_X = 'C_X'
O_E = 'O_E' # Other
O_X = 'O_X'
IFX = 'IFX' # leaving if


# 'States'
BTT = 'BTT'  # stack bottom
CTT = 'CTT'  # bottom of regular class
FTT = 'FTT'  # bottom of regular method/function
IFT = 'IFT'  # if.test attribute
IFB = 'IFB'  # if.body attribute
IFO = 'IFO'  # if.orelse attribute

# stack actions
NOOP = lambda: lambda stack: stack
PUSH = lambda items: lambda stack: stack + items

# Transition table for cobertura.dtd
TBL = {
        (M_E, BTT): PUSH([BTT]),
        (M_X, BTT): PUSH([BTT]),

        (F_E, BTT): PUSH([BTT, F_E]), # module-level function
        (F_E, CTT): PUSH([CTT, FTT]), # method
        (F_E, FTT): PUSH([FTT, F_E]), # function within method
        (F_E, F_E): PUSH([F_E, F_E]), # function within function
        (F_E, C_E): PUSH([C_E, F_E]), # function within nested class
        (F_E, O_E): PUSH([O_E, F_E]), # function within other statement
        (F_E, IFB): PUSH([IFB, F_E]), # entering function definition within if.body
        (F_E, IFO): PUSH([IFO, F_E]), # entering function definition within if.orelse
        (F_X, FTT): NOOP(),           # leaving method
        (F_X, F_E): NOOP(),           # leaving any nested function

        (C_E, BTT): PUSH([BTT, CTT]), # entering regular class
        (C_E, CTT): PUSH([CTT, C_E]), # entering class nested in regular class
        (C_E, FTT): PUSH([FTT, C_E]), # entering class within a method
        (C_E, C_E): PUSH([C_E, C_E]), # entering class within a class
        (C_E, F_E): PUSH([F_E, C_E]), # entering class within a function
        (C_E, O_E): PUSH([O_E, C_E]), # entering class within other statement
        (C_X, CTT): NOOP(),           # leaving regular class
        (C_X, C_E): NOOP(),           # leaving any nested function
        (C_E, IFB): PUSH([IFB, C_E]), # entering class definition within if.body
        (C_E, IFO): PUSH([IFO, C_E]), # entering class definition within if.orelse
        
        (O_E, BTT): PUSH([BTT, O_E]), # entering other module-level statement
        (O_E, FTT): PUSH([FTT, O_E]), # entering other method-level statement
        (O_E, CTT): PUSH([CTT, O_E]), # entering other regular-class-level statement
        (O_E, F_E): PUSH([F_E, O_E]), # entering other (nested-)function-level statement
        (O_E, C_E): PUSH([C_E, O_E]), # entering other nested-class-level statement
        (O_E, O_E): PUSH([O_E, O_E]), # entering other (nested) statemetn
        (O_E, IFT): PUSH([IFT, O_E]), # entering other statement within if.test
        (O_E, IFB): PUSH([IFB, O_E]), # entering other statement within if.body
        (O_E, IFO): PUSH([IFO, O_E]), # entering other statement within if.orelse
        (O_X, O_E): NOOP(),           # leaving other (nested) statement
        (O_X, FTT): PUSH([FTT]),
        (O_X, CTT): PUSH([CTT]),
        (O_X, BTT): PUSH([BTT]),

        (IFT, BTT): PUSH([BTT, IFT]), # entering if statement within a module line
        (IFT, FTT): PUSH([FTT, IFT]), # entering if statement within a regular method line
        (IFT, CTT): PUSH([CTT, IFT]), # entering if statement within a regular class line
        (IFT, C_E): PUSH([C_E, IFT]), # entering if statement within a nested class line
        (IFT, F_E): PUSH([F_E, IFT]), # entering if statement within a nested function line
        (IFT, O_E): PUSH([O_E, IFT]), # entering if statement within a (sub-)statement line
        (IFT, IFB): PUSH([IFB, IFT]), # entering nested if statement from within if.body
        (IFT, IFO): PUSH([IFO, IFT]), # entering nested if statement from within if.orelse
        (IFB, IFT): PUSH([IFB]),      # entering if.body
        (IFO, IFB): PUSH([IFO]),      # entering if.orelse
        (IFX, IFB): NOOP(),           # leaving if statement from within if.body (no orelse present)
        (IFX, IFO): NOOP(),           # leaving if statement from within of.orelse

}

class PushDownAutomaton(object):

    # by default, use `lambda event, stack_event: None' callbacks for any event
    def __init__(self, stack=None, callbacks=collections.defaultdict(lambda: lambda event, stack_event: None)):
        if stack is None:
            stack = [BTT]
        self.reset(stack)
        self.callbacks = callbacks

    def reset(self, stack=None):
        if stack is None:
            stack = [BTT]
        self.stack = stack

    def __repr__(self):
        return type(self).__name__ + '(stack=%r)'% self.stack

    def __call__(self, event):
        stack_event = self.stack.pop()
        # perform callback
        self.callbacks[(event, stack_event)](event, stack_event)
        # perform stack manipulation based on the transition table
        self.stack = TBL[(event, stack_event)](self.stack)
        import pprint
        #print pprint.pformat(self.stack), event


class Line(object):
    prefix = " "
    def __init__(self, node, depth=0):
        self.node = node
        self.depth = depth

    def __repr__(self):
        return type(self).__name__ + "(%r, depth=%r)" % (self.node, self.depth)
        print self

    def __str__(self):
        return self.prefix * self.depth + type(self).__name__ + ": %s" % self.node.lineno

    def __call__(self, node):
        '''print line in case node linenos differ; update self.node'''
        if not hasattr(self.node, "lineno"):
            lineno = 0
        else:
            lineno = self.node.lineno
        if not hasattr(node, "lineno"):
            return
        if lineno != node.lineno:
           # new line
           self.node = node
           print self

class ModuleLine(Line):
    pass
class ClassLine(Line):
    pass

class MethodLine(Line):
    pass

class IfLine(Line):
    pass

class LineStatus(object):
    def __init__(self):
        self.set_stack = []

    @property
    def top_set(self):
        return self.set_stack[-1]

    @top_set.setter
    def top_set(self, other):
        self.set_stack[-1] = other

    @property
    def depth(self):
        return len(self.set_stack)

    def push_set(self):
        self.set_stack.append(set())

    def pop_set(self):
        return self.set_stack.pop()

    def add_line(self, lineno):
        self.top_set.add(lineno)

    @property
    def info(self):
        return self.depth * " " + "...total %r lines" % len(self.top_set)

class Visitor(ast.NodeVisitor):

    def __init__(self, *args, **kvs):
        callbacks = {
            (M_E, BTT): self.init_module,
            (M_X, BTT): self.exit_module,
            (C_E, BTT): self.init_class,
            (F_E, CTT): self.init_method,
            (C_X, CTT): self.exit_class,
            (F_X, FTT): self.exit_method,
            (IFT, BTT): self.init_if,
            (IFT, CTT): self.init_if,
            (IFT, FTT): self.init_if,
            (IFT, F_E): self.init_if,
            (IFT, C_E): self.init_if,
            (IFT, O_E): self.init_if,
            (IFT, IFT): self.init_if,
            (IFT, IFB): self.init_if,
            (IFT, IFO): self.init_if,
            (IFX, IFB): self.exit_if,
            (IFX, IFO): self.exit_if,

        }
        self.callbacks = collections.defaultdict( \
            lambda: self.line_handler,
            callbacks.items()
        )
        self.node = None
        self.line = None
        self.pda = PushDownAutomaton(callbacks=self.callbacks)
        self.line_status = LineStatus()
        super(Visitor, self).__init__(*args, **kvs)
        
    def visit_Module(self, node):
        self.generic_visit(node, (M_E, M_X))

    def visit_FunctionDef(self, node):
        self.generic_visit(node, (F_E, F_X))

    def visit_ClassDef(self, node):
        self.generic_visit(node, (C_E, C_X))

    def visit_If(self, node):
        # need to distinguish between test/body/orelse if statement subtrees
        self.node = node
        self.pda(IFT)
        super(Visitor, self).generic_visit(node.test)
        self.pda(IFB)
        for sub_node in node.body:
            super(Visitor, self).generic_visit(sub_node)
        if node.orelse is not None:
            self.pda(IFO)
            for sub_node in node.orelse:
                super(Visitor, self).generic_visit(sub_node)
        self.pda(IFX)

    def generic_visit(self, node, events=(O_E, O_X)):
        self.node = node
        #print "::%s" % type(self.node)
        self.pda(events[0])
        super(Visitor, self).generic_visit(node)
        self.pda(events[1])

    def line_handler(self, event, stack_event):
        self.line(self.node)
        if hasattr(self.node, 'lineno'):
            self.line_status.add_line(self.node.lineno)

    def init_module(self, event, stack_event):
        print "Module:"
        self.line_status.push_set()
        self.line = ModuleLine(self.node)

    def exit_module(self, event, stack_event):
        print self.line_status.info
        self.line_status.pop_set()
        self.line(self.node)

    def init_class(self, event, stack_event):
        print " Class: %s at %s" % (self.node.name, self.node.lineno)
        self.line_status.push_set()
        self.line = ClassLine(self.node, self.line_status.depth)

    def exit_class(self, event, stack_event):
        print self.line_status.info
        self.line_status.pop_set()
        self.line = ModuleLine(self.node, self.line_status.depth)

    def init_method(self, event, stack_event):
        print "  Method: %s at %s" % (self.node.name, self.node.lineno)
        self.line_status.push_set()
        self.line = MethodLine(self.node, self.line_status.depth)

    def exit_method(self, event, stack_event):
        print self.line_status.info
        self.line_status.pop_set()
        self.line = ClassLine(self.node, self.line_status.depth)

    def init_if(self, event, stack_event):
        self.line = IfLine(self.node, self.line_status.depth)
        self.line_status.push_set()
        pass

    def exit_if(self, event, stack_event):
        print self.line_status.info
        self.line_status.pop_set()
        pass


###
try:
    with open("sample.py") as fd:
        src = fd.read()
except Exception as e:
    print "Can't read sample.py: %s" % e.message
    sys.exit(2)

tree = ast.parse(src)
print src
#import astpp
#print astpp.dump(tree, annotate_fields=True, include_attributes=True)
visitor = Visitor()
visitor.visit(tree)

