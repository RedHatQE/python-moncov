#!/usr/bin/pytho
import ast
import collections

# *_[EX] events: Enter eXit
M_E = 'M_E' # Module
M_X = 'M_X'
F_E = 'F_E' # Function
F_X = 'F_X'
C_E = 'C_E' # Class
C_X = 'C_X'
O_E = 'O_E' # Other
O_X = 'O_X'


BTT = 'BTT'   # stack bottom
CTT = 'CTT'  # bottom of regular class
FTT = 'FTT'  # bottom of regular method/function

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
        
        (O_E, BTT): PUSH([BTT, O_E]), # entering other module-level statement
        (O_E, FTT): PUSH([FTT, O_E]), # entering other method-level statement
        (O_E, CTT): PUSH([CTT, O_E]), # entering other regular-class-level statement
        (O_E, F_E): PUSH([F_E, O_E]), # entering other (nested-)function-level statement
        (O_E, C_E): PUSH([C_E, O_E]), # entering other nested-class-level statement
        (O_E, O_E): PUSH([O_E, O_E]), # entering other (nested) statemetn
        (O_X, O_E): NOOP(),            # leaving other (nested) statement
        (O_X, FTT): PUSH([FTT]),
        (O_X, CTT): PUSH([CTT]),
        (O_X, BTT): PUSH([BTT]),
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
        #import pprint
        #print pprint.pformat(self.stack), event


class Line(object):
    def __init__(self, node):
        self.node = node

    def __repr__(self):
        return type(self).__name__ + "(%r)" % self.node
        print self

    def __str__(self):
        return type(self).__name__ + ": %s" % self.node.lineno

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

class Visitor(ast.NodeVisitor):

    def __init__(self, *args, **kvs):
        callbacks = {
            (M_E, BTT): self.init_module,
            (M_X, BTT): self.exit_module,
            (C_E, BTT): self.init_class,
            (F_E, CTT): self.init_method,
            (C_X, CTT): self.exit_class,
            (F_X, FTT): self.exit_method,
        }
        self.callbacks = collections.defaultdict( \
            lambda: self.line_handler,
            callbacks.items()
        )
        self.node = None
        self.line = None
        self.pda = PushDownAutomaton(callbacks=self.callbacks)
        super(Visitor, self).__init__(*args, **kvs)
        
    def visit_Module(self, node):
        self.generic_visit(node, (M_E, M_X))

    def visit_FunctionDef(self, node):
        self.generic_visit(node, (F_E, F_X))

    def visit_ClassDef(self, node):
        self.generic_visit(node, (C_E, C_X))

    def generic_visit(self, node, events=(O_E, O_X)):
        self.node = node
        self.pda(events[0])
        super(Visitor, self).generic_visit(node)
        self.pda(events[1])

    def line_handler(self, event, stack_event):
        if self.line is not None:
            self.line(self.node)

    def init_module(self, event, stack_event):
        self.line = ModuleLine(self.node)

    def exit_module(self, event, stack_event):
        self.line(self.node)

    def init_class(self, event, stack_event):
        self.line = ClassLine(self.node)

    def exit_class(self, event, stack_event):
        self.line = ModuleLine(self.node)

    def init_method(self, event, stack_event):
        self.line = MethodLine(self.node)

    def exit_method(self, event, stack_event):
        self.line = ClassLine(self.node)


###
src = \
'''
import yaml

print "Hello, world!"

def my_func(some, args):
    pass

def parent_func(what, ever, args):
    """some doc string"""
    def baby_func():
        pass

class MyClass(object):
    class ANestedClass(object):
        def __init__(self):
            pass
        def complex_m(self):
            def inner():
                pass
            class Burried(object):
               pass
    def __init__(self):
        print "Ahoj"
        print "Ahoj me"

    @classmethod
    def zoo_metdhod(cls):
        def chicken_method():
            def egg_method(*args, **kvs):
                pass
            egg_method(yolk='yellow')
        chicken_method()

print "Good Bye!"

class Foo(object):
    mcls = MyClass()

print "Really, Good Bye!"

'''

tree = ast.parse(src)
print src
# import astpp
#print astpp.dump(tree, annotate_fields=True, include_attributes=True)
visitor = Visitor()
visitor.visit(tree)

