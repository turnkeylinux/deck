class A:
    def foo(self):
        print "foo"

    def bar(self):
        self.__class__().foo()
    
a = A()
a.foo()
a.bar()
