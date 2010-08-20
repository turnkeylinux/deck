class RigidVal:
    class Error(Exception):
        pass
    
    def __init__(self):
        self.val = None

    def set(self, val):
        if self.val is not None:
            raise self.Error("value already set")
        self.val = val

    def get(self):
        return self.val

def foo():
    val = RigidVal()
    try:
        val.set(666)
        val.set(111)
    except val.Error:
        print "warning: attempted to set value set more than once"
        
    print "val: " + `val.get()`

foo()

