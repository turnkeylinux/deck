class Var:
    def __init__(self):
        self.var = None

def foo():
    class_var = Var()
    normal_var = None
    
    def set_var(val):
        class_var.var = val
        normal_var = val

    set_var(666)
    print "class_var = " + `class_var.var`
    print "normal_var = " + `normal_var`

foo()

