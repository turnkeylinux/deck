def foo():
    var = None
    def set_var(val):
        var = val
    set_var(666)
    print "var = " + `var`

foo()

