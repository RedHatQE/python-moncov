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
        
        i = 0
        while i < 3:
            if i == 2:
                pass
            for j in [1, 2, 3]:
                print j
            i += 1
        
        if True:
                pass
        else:
            pass

print "Good Bye!"

for i in range(2):
    pass
else:
    pass
    
i = 0
while i < 3:
    if i == 2:
        pass
    for j in [1, 2, 3]:
        print j
    i += 1

for j in [1, 2, 3]:
    if j == 1:
        print "Makaka!"
    else:
        i = 1
        while i !=3:
            i+=1
        print j

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

while i < 10:
    j = 0
    while j < 5:
        print j
        j += 1
        for k in [1, 2, 3, 4, 5]:
            for p in [1,2,3]:
                print k, p
    i +=1

