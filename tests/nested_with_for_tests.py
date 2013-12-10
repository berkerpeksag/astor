class A(object):
    pass

class B(object):
    pass

def test():
    with A() as a:
        with B() as b:
            print ("test1")

def test2():
    with A() as a, B() as b:
        print ("test2")
