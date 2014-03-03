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
        if True:
                pass
        else:
            pass

print "Good Bye!"

for i in range(2):
    pass
else:
    pass

class Foo(object):
    mcls = MyClass()

if True:
    def f():
        pass
    if True:
        class c (object):
            pass
        if True:
            pass
        elif False:
            class cc(object):
                def __init__(self):
                    pass
    else:
        pass
else:
    pass

if True:
    3
else:
    4

print "Really, Good Bye!"


