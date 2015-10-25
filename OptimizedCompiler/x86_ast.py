
#from compiler.ast import *
from compiler.ast import *


class Pushl(Node):
	def __init__(self, node):
		self.node = node
	def __repr__(self):
		return "Push(%s)" % (repr(self.node))


class Popl(Node):
	def __init__(self, node):
		self.node = node
	def __repr__(self):
		return "Popl(%s)" % (repr(self.node))


class Movl(Node):
	def __init__(self, left, right):
		self.left  = left
		self.right = right
	def __repr__(self):
		return "Movl(%s, %s)" % (repr(self.left), repr(self.right))


class Addl(Node):
	def __init__(self, left, right):
		self.left  = left
		self.right = right
	def __repr__(self):
		return "Addl(%s, %s)" % (repr(self.left), repr(self.right))


class Call(Node):
	def __init__(self, node):
		self.node = node
	def __repr__(self):
		return "Call(%s)" % (repr(self.node))


class PrintX86(Node):
	def __init__(self, node):
		self.node = node
	def __repr__(self):
		return "PrintX86(%s)" % (repr(self.node))


class Subl(Node):
	def __init__(self, left, right):
		self.left  = left
		self.right = right
	def __repr__(self):
		return "(%s, %s)" % (repr(self.left), repr(self.right))


class Negl(Node):
	def __init__(self, node):
		self.node = node
	def __repr__(self):
		return "Negl(%s)" % (repr(self.node))


class NOOP(Node):
	def __init__(self, node):
		self.node = node
	def __rep__(self):
		return "NOOP(%s)" % (repr(self.node))

class Cmpl(Node):
	def __init__(self, op1, op2):
		self.op1 = op1
	        self.op2 = op2
	def __rep__(self):
		return "Cmpl(%s)" % (repr(self.op1), repr(self.op2))

class Andl(Node):
	def __init__(self, op1, op2):
		self.op1 = op1
	        self.op2 = op2
	def __rep__(self):
		return "Andl(%s)" % (repr(self.op1), repr(self.op2))

class Orl(Node):
	def __init__(self, op1, op2):
		self.op1 = op1
	        self.op2 = op2
	def __rep__(self):
		return "Orl(%s)" % (repr(self.op1), repr(self.op2))

class Notl(Node):
	def __init__(self, expr):
		self.expr = expr
	def __rep__(self):
		return "Notl(%s)" % (repr(self.expr))

class JmpEqual(Node):
	def __init__(self, label):
		self.label = label
	def __rep__(self):
		return "JmpEqual(%s)" % (repr(self.label))

class JmpTo(Node):
	def __init__(self, label):
		self.label = label
	def __rep__(self):
		return "JmpTo(%s)" % (repr(self.label))

class Label(Node):
	def __init__(self, label):
		self.label = label
	def __rep__(self):
		return "JmpTo(%s)" % (repr(self.label))

class x86Compare(Node):
    def __init__(self, expr, ops, name):
        self.expr = expr
        self.ops = ops
        self.name = name
    def __rep__(self):
        return "x86Compare(%s, %s, %s)" % (repr(self.expr), repr(self.ops), repr(self.name))
