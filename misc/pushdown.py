#!/usr/bin/python
import ast
import collections
import sys
import fractions

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
FOX = 'FOX' # leaving for
WHX = 'WHX' # leaving while


# 'States'
BTT = 'BTT'  # stack bottom
CTT = 'CTT'  # bottom of regular class
FTT = 'FTT'  # bottom of regular method/function
IFT = 'IFT'  # if.test attribute
IFB = 'IFB'  # if.body attribute
IFO = 'IFO'  # if.orelse attribute
FOT = 'FOT'  # for.test attribute
FOB = 'FOB'  # for.body attribute
WHT = 'WHT'  # while.test attribute
WHB = 'WHB'  # while.body attribute

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
        (F_E, FOB): PUSH([FOB, F_E]), # entering function definition within for.body
        (F_E, WHB): PUSH([WHB, F_E]), # entering function definition within while.body
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
        (C_E, FOB): PUSH([FOB, C_E]), # entering class definition within for.body
        (C_E, WHB): PUSH([WHB, C_E]), # entering class definition within while.body
        (C_E, IFO): PUSH([IFO, C_E]), # entering class definition within if.orelse

        (O_E, BTT): PUSH([BTT, O_E]), # entering other module-level statement
        (O_E, FTT): PUSH([FTT, O_E]), # entering other method-level statement
        (O_E, CTT): PUSH([CTT, O_E]), # entering other regular-class-level statement
        (O_E, F_E): PUSH([F_E, O_E]), # entering other (nested-)function-level statement
        (O_E, C_E): PUSH([C_E, O_E]), # entering other nested-class-level statement
        (O_E, O_E): PUSH([O_E, O_E]), # entering other (nested) statemetn
        (O_E, IFT): PUSH([IFT, O_E]), # entering other statement within if.test
        (O_E, IFB): PUSH([IFB, O_E]), # entering other statement within if.body
        
        (O_E, FOT): PUSH([FOT, O_E]), # entering other statement within for.test
        (O_E, FOB): PUSH([FOB, O_E]), # entering other statement within for.body
        
        (O_E, WHT): PUSH([WHT, O_E]), # entering other statement within while.test
        (O_E, WHB): PUSH([WHB, O_E]), # entering other statement within while.body
        
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
        
        (IFT, FOB): PUSH([FOB, IFT]), # entering nested if statement from within for.body
        (IFT, WHB): PUSH([WHB, IFT]), # entering nested if statement from within while.body
        
        (IFT, IFO): PUSH([IFO, IFT]), # entering nested if statement from within if.orelse
        (IFB, IFT): PUSH([IFB]),      # entering if.body
        (IFO, IFB): PUSH([IFO]),      # entering if.orelse
        (IFX, IFB): NOOP(),           # leaving if statement from within if.body (no orelse present)
        (IFX, IFO): NOOP(),           # leaving if statement from within of.orelse
        (IFX, FOB): NOOP(),           # leaving if statement from within for.body 
        (IFX, WHB): NOOP(),           # leaving if statement from within while.body
        (IFX, IFO): NOOP(),           # leaving if statement from within if.orelse
        
        
        
        (FOT, BTT): PUSH([BTT, FOT]), # entering for statement within a module line
        (FOT, FTT): PUSH([FTT, FOT]), # entering for statement within a regular method line
        (FOT, CTT): PUSH([CTT, FOT]), # entering for statement within a regular class line
        (FOT, C_E): PUSH([C_E, FOT]), # entering for statement within a nested class line
        (FOT, F_E): PUSH([F_E, FOT]), # entering for statement within a nested function line
        (FOT, O_E): PUSH([O_E, FOT]), # entering for statement within a (sub-)statement line
        (FOT, FOB): PUSH([FOB, FOT]), # entering nested for statement from within for.body
        (FOT, IFB): PUSH([IFB, FOT]), # entering nested for statement from within if.body
        (FOT, WHB): PUSH([WHB, FOT]), # entering nested for statement from within while.body
        (FOT, IFO): PUSH([IFO, FOT]), # entering nested for statement from within if.orelse
        (FOB, FOT): PUSH([FOB]),      # entering for.body
        (FOX, FOB): NOOP(),           # leaving for statement from within for.body 
        (FOX, IFB): NOOP(),           # leaving for statement from within if.body 
        (FOX, IFO): NOOP(),           # leaving for statement from within if.orelse 
        (FOX, WHB): NOOP(),           # leaving for statement from within while.body 
        
        
        (WHT, BTT): PUSH([BTT, WHT]), # entering while statement within a module line
        (WHT, FTT): PUSH([FTT, WHT]), # entering while statement within a regular method line
        (WHT, CTT): PUSH([CTT, WHT]), # entering while statement within a regular class line
        (WHT, C_E): PUSH([C_E, WHT]), # entering while statement within a nested class line
        (WHT, F_E): PUSH([F_E, WHT]), # entering while statement within a nested function line
        (WHT, O_E): PUSH([O_E, WHT]), # entering while statement within a (sub-)statement line
        (WHT, FOB): PUSH([FOB, WHT]), # entering nested while statement from within for.body
        (WHT, IFB): PUSH([IFB, WHT]), # entering nested while statement from within if.body
        (WHT, WHB): PUSH([WHB, WHT]), # entering nested while statement from within while.body
        (WHT, IFO): PUSH([IFO, WHT]), # entering nested while statement from within if.orelse
        (WHB, FOT): PUSH([FOB]),      # entering while.body
        (WHB, WHT): PUSH([WHB]),      # entering while.body from within while.test
        (WHX, FOB): NOOP(),           # leaving while statement from within for.body 
        (WHX, IFB): NOOP(),           # leaving while statement from within if.body 
        (WHX, IFO): NOOP(),           # leaving while statement from within if.orelse 
        (WHX, WHB): NOOP(),           # leaving while statement from within while.body 
        (WHX, WHT): NOOP(),           # leaving while statement from within while.body 

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


class Stack(object):
    def __init__(self, data=[]):
        self.data = data

    @property
    def top(self):
        return self.data[-1]

    @top.setter
    def top(self, other):
        self.data[-1] = other

    @property
    def depth(self):
        return len(self.data)

    def push(self, item):
        self.data.append(item)

    def pop(self):
        return self.data.pop()


class Rate(fractions.Fraction):

    def __new__(cls, numerator=0, denominator=None):
        '''avoid reduction'''
        self = super(Rate, cls).__new__(cls, numerator, denominator)
        if denominator is None:
            return self
        gcd = fractions.gcd(numerator, denominator)
        self._numerator *= gcd
        self._denominator *= gcd
        return self

    def __or__(self, other):
        '''grow the portion and the pie size'''
        return type(self)(self.numerator + other.numerator,
                        self.denominator + other.denominator)

    def __and__(self, other):
        '''grow the portion and pie size if both self and other are not zero'''
        if self != 0 and other != 0:
            return self | other
        elif self == 0 and other != 0:
            return other
        elif self !=0 and other == 0:
            return self
        else:
            return Rate(0)


    def __repr__(self):
        return '%s(%r, %r)' % (type(self).__name__, self.numerator, self.denominator)

    @classmethod
    def as_fraction(cls, rate):
        '''return a fraction created out of a rate instance'''
        return fractions.Fraction(rate.numerator, rate.denominator)


Line = collections.namedtuple('Line', ['lineno'])
IfLine = collections.namedtuple('IfLine', ['lineno'])
ForLine = collections.namedtuple('ForLine', ['lineno'])
WhileLine = collections.namedtuple('WhileLine', ['lineno'])
MethodLine = collections.namedtuple('MethodLine', ['lineno'])
ClassLine = collections.namedtuple('ClassLine', ['lineno'])
ModuleLine = collections.namedtuple('ModuleLine', ['lineno'])

class Status(object):
    lineno = None
    linetype = None
    lines = None
    line_rate = None
    branch_rate = None
    hits = None
    linetype = None
    def __init__(self, lineno=0, lines=set(), hits=set(), line_rate=Rate(0),
            branch_rate=Rate(0), linetype=ModuleLine):
        self.linetype = linetype
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
        self._lines = other_set
        self._lines.add(self.line)

    def merge(self, other):
        # merge statuses <<=
        assert type(self) is type(other)
        self.lines |= other.lines
        self.hits |= other.hits
        self.branch_rate &= other.branch_rate
        self.line_rate |= other.line_rate

    @property
    def line(self):
        return self.linetype(lineno=self.lineno)

    def add_line(self, lineno):
        '''add another line and update line rate'''
        line = self.linetype(lineno)
        if line in self.lines:
            # already counted
            return
        if lineno in self.hits:
            # executed line
            self.line_rate |= Rate(1, 1)
        else:
            self.line_rate |= Rate(0, 1)
        self.lines.add(line)

    def __repr__(self):
        return '%r(lineno=%r, lines=%r, hits=%r, line_rate=%r, branch_rate=%r)' % (
                type(self), self.lineno, self.lines, self.hits, self.line_rate,
                self.branch_rate)

    def __str__(self):
        return 'Status: line_rate = %s, branch_rate = %s' % (self.line_rate, self.branch_rate)


class Visitor(ast.NodeVisitor):

    def __init__(self, hit_count={}):
        callbacks = {
            (M_E, BTT): self.init_module,
            (M_X, BTT): self.exit_module,
            (C_E, BTT): self.init_class,
            (F_E, CTT): self.init_method,
            (C_X, CTT): self.exit_nested,
            (F_X, FTT): self.exit_nested,
            
            
            (IFT, BTT): self.init_if,
            (IFT, CTT): self.init_if,
            (IFT, FTT): self.init_if,
            (IFT, F_E): self.init_if,
            (IFT, C_E): self.init_if,
            (IFT, O_E): self.init_if,
            (IFT, IFT): self.init_if,
            (IFT, IFB): self.init_if,
            (IFT, IFO): self.init_if,
            (IFT, WHB): self.init_if,
            (IFT, FOB): self.init_if,

            
            
            (FOT, BTT): self.init_for,
            (FOT, CTT): self.init_for,
            (FOT, FTT): self.init_for,
            (FOT, F_E): self.init_for,
            (FOT, C_E): self.init_for,
            (FOT, O_E): self.init_for,
            (FOT, IFT): self.init_for,
            (FOT, IFB): self.init_for,
            (FOT, IFO): self.init_for,            
            (FOT, FOT): self.init_for,
            (FOT, FOB): self.init_for,
            (FOT, WHT): self.init_for,
            (FOT, WHB): self.init_for,
            
            
            (WHT, BTT): self.init_while,
            (WHT, CTT): self.init_while,
            (WHT, FTT): self.init_while,
            (WHT, F_E): self.init_while,
            (WHT, C_E): self.init_while,
            (WHT, O_E): self.init_while,
            (WHT, IFT): self.init_while,
            (WHT, IFB): self.init_while,
            (WHT, IFO): self.init_while,            
            (WHT, FOT): self.init_while,
            (WHT, FOB): self.init_while,
            (WHT, WHT): self.init_while,
            (WHT, WHB): self.init_while,
            
            
            (IFX, IFB): self.exit_nested,
            (IFX, IFO): self.exit_nested,
            (IFX, FOB): self.exit_nested,
            (IFX, WHB): self.exit_nested,
            
            
            
            (FOX, IFB): self.exit_nested,
            (FOX, IFO): self.exit_nested,
            (FOX, FOB): self.exit_nested,
            (FOX, WHB): self.exit_nested,
            
            (WHX, IFB): self.exit_nested,
            (WHX, IFO): self.exit_nested,
            (WHX, FOB): self.exit_nested,    
            (WHX, WHB): self.exit_nested,

        }
        self.callbacks = collections.defaultdict( \
            lambda: self.line_handler,
            callbacks.items()
        )
        self.pda = PushDownAutomaton(callbacks=self.callbacks)
        self.node = None
        # hit_count is a mapping: lineno->line_hits
        self.hit_count = hit_count
        # set of lines explored during parsing
        self.lines = set()
        # all hit/executed lines
        self.hits = set(self.hit_count.keys())
        self.report = None

        super(Visitor, self).__init__()

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
        self.visit(node.test)
        self.pda(IFB)
        for sub_node in node.body:
            self.visit(sub_node)
        if node.orelse:
            self.pda(IFO)
        for sub_node in node.orelse:
            self.visit(sub_node)
        self.pda(IFX)
        
    def visit_For(self, node):
        self.node = node
        self.pda(FOT)
        self.visit(node.target)
        self.visit(node.iter)
        self.pda(FOB)
        for subnode in node.body + node.orelse:
            self.visit(subnode)
        #self.add_branch(node)
        self.pda(FOX)
        
    def visit_While(self, node):
        self.node = node
        self.pda(WHT)
        self.visit(node.test)
        self.pda(WHB)
        for subnode in node.body + node.orelse:
            self.visit(subnode)
        #self.add_branch(node)
        self.pda(WHX)        

    def generic_visit(self, node, events=(O_E, O_X)):
        self.node = node
        #print "::%s" % type(self.node)
        self.pda(events[0])
        super(Visitor, self).generic_visit(node)
        self.pda(events[1])

    def line_handler(self, event, stack_event):
        if hasattr(self.node, 'lineno'):
            self.report.top.add_line(self.node.lineno)

    def init_module(self, event, stack_event):
        self.report = Stack([Status(lineno=0, hits=self.hits, linetype=ModuleLine)])

    def exit_module(self, event, stack_event):
        pass

    def init_class(self, event, stack_event):
        self.report.push(Status(lineno=self.node.lineno, hits=self.hits, linetype=ClassLine))

    def exit_nested(self, event, stack_event):
        status = self.report.pop()
        self.report.top.merge(status)

    def init_method(self, event, stack_event):
        self.report.push(Status(lineno=self.node.lineno, hits=self.hits, linetype=MethodLine))

    def init_if(self, event, stack_event):
        self.report.push(Status(lineno=self.node.lineno, hits=self.hits, linetype=IfLine, branch_rate=Rate(1, 2)))

    def init_for(self, event, stack_event):
        self.report.push(Status(lineno=self.node.lineno, linetype=ForLine, hits=self.hits, branch_rate=Rate(1, 2)))

    def init_while(self, event, stack_event):
        self.report.push(Status(lineno=self.node.lineno, linetype=WhileLine, hits=self.hits, branch_rate=Rate(1, 2)))



    @property
    def status(self):
        '''return top of self.report stack'''
        return self.report.top


###
try:
    with open("sample.py") as fd:
        src = fd.read()
except Exception as e:
    print "Can't read sample.py: %s" % e.message
    sys.exit(2)

tree = ast.parse(src)
#print src
#import astpp
#print astpp.dump(tree, annotate_fields=True, include_attributes=True)
visitor = Visitor(hit_count={66: 3})
visitor.visit(tree)

import pprint
print pprint.pformat(visitor.status.lines), len(visitor.status.lines)
print visitor.status

