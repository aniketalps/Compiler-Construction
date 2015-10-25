from compiler.ast import *

# Create closure
class CreateClosure(Node):
	def __init__(self, name, argnames):
		self.name = name
		self.argnames = argnames
	def __repr__(self):
		return "CreateClosure(%s, %s)" % \
				(repr(self.name), repr(self.argnames))

class FunctionCl(Node):
	def __init__(self, name, fvs, params, code):
		self.fvs = fvs
		self.params = params
		self.code = code
	def __repr__(self):
		return "FunctionCl(%s, %s, %s)" % \
				(repr(self.fvs), repr(self.params), repr(self.code))
