import nose
import logging
l = logging.getLogger("claripy.test")

import claripy.backends, claripy.expressions

def test_expressions():
    a = claripy.expressions.AbstractExpression(op='BitVec', args=('x', 32), variables={'x'}, symbolic=True)
    z = claripy.backends.BackendZ3()
    b = a.actualize(z)
    c = b+b
    nose.tools.assert_equal(str(c), 'ActualExpression(x + x)')
    d = c.abstract().actualize(z)
    nose.tools.assert_equal(str(d), str(c))

if __name__ == '__main__':
    test_expressions()
    print "WOO"