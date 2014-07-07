import logging
l = logging.getLogger("claripy.backends.backend_z3")

# import and set up Z3
import os
import z3
if "Z3PATH" in os.environ:
	z3_path = os.environ["Z3PATH"]
elif "VIRTUAL_ENV" in os.environ:
	virtual_env = os.environ["VIRTUAL_ENV"]
	z3_path = virtual_env + "/lib/"
else:
	z3_path = "/opt/python/lib/"
z3.init(z3_path + "libz3.so")

class BackendZ3(object):
	whitelist = [ 'If', 'And', 'Not', 'Or', 'UGE', 'ULE', 'UGT', 'ULT', 'BoolVal', 'BitVec', 'BitVecVal', 'Concat', 'Extract', 'LShR', 'SignExt', 'ZeroExt' ]

	def op(self, op_name):
		if op_name not in self.whitelist:
			raise Exception("unknown op %s requested from %s" % (op_name, self.__class__.__name__))
		return getattr(z3, op_name)

	def abstract(self, z):
		children = [ self.abstract(c) for c in z.children() ]
		name = z.decl().name()

		symbolic = any([ c.symbolic if isinstance(c, Expression) else False for c in children ])
		variables = set()
		for c in children:
			if isinstance(c, Expression):
				variables |= c.variables

		if len(children) == 0:
			if z.__class__ == z3.BitVecRef:
				op = "BitVec"
				args = (name, z.size())
				symbolic = True
				variables = { name }
			elif z.__class__ == z3.BitVecNumRef:
				op = "BitVecVal"
				args = (z.as_long(), z.size())
			elif name == 'true':
				op = "BoolVal"
				args = (True,)
			elif name == 'false':
				op = "BoolVal"
				args = (False,)
			else:
				raise TypeError("Unable to wrap type %s", z.__class__.__name__)
		else:
			if name == 'extract':
				# GAH
				args = [ int(non_decimal.sub('', i)) for i in str(z).split(',')[:2] ] + children
			elif name in ('sign_extend', 'zero_extend'):
				args = int(str(z).split('(')[1].split(', ')[0]) + children
			elif name == 'zero_extend':
				args = int(str(z).split('(')[1].split(', ')[0]) + children
			else:
				if len(children) != 2 and not (name == 'bvnot' and len(children) == 1) and not (name == 'concat' and len(children) > 0):
					raise TypeError("%d children received for operation %s!" % (len(children), name))
				args = children
			op = function_map[name]

		return AbstractExpression(op=op, args=args, variables=variables, symbolic=symbolic)

#
# this is for the actual->abstract conversion above
#

import re
non_decimal = re.compile(r'[^\d.]+')

function_map = { }
function_map['bvadd'] = '__add__'
function_map['bvxor'] = '__and__'
function_map['bvsdiv'] = '__div__'
function_map['bvsdiv_i'] = '__div__' # TODO: make sure this is correct
function_map['bvnot'] = '__invert__'
function_map['bvshl'] = '__lshift__'
function_map['bvsmod'] = '__mod__'
function_map['bvmul'] = '__mul__'
function_map['distinct'] = '__ne__'
function_map['bvneg'] = '__neg__'
function_map['bvor'] = '__or__'
function_map['bvashr'] = '__rshift__'
function_map['bvsub'] = '__sub__'
function_map['bvxor'] = '__xor__'
function_map['='] = '__eq__'
function_map['bvsgt'] = '__gt__'
function_map['bvsge'] = '__ge__'
function_map['bvslt'] = '__lt__'
function_map['bvsle'] = '__le__'
function_map['bvuge'] = 'z3.UGE'
function_map['bvugt'] = 'z3.UGT'
function_map['bvule'] = 'z3.ULE'
function_map['bvult'] = 'z3.ULT'
function_map['concat'] = 'z3.Concat'
function_map['extract'] = 'z3.Extract'
function_map['or'] = 'z3.Or'
function_map['and'] = 'z3.And'
function_map['not'] = 'z3.Not'
function_map['if'] = 'z3.If'
function_map['bvlshr'] = 'z3.LShR'

from ..expressions import AbstractExpression, Expression
