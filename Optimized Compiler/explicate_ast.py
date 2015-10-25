from compiler.ast import *

class GetTag(Node):
  def __init__(self, typ, arg):
    self.typ = typ
    self.arg = arg
  def __repr__(self):
    return "GetTag(%s, %s)" % (repr(self.typ), repr(self.arg))

class InjectFrom(Node):
  def __init__(self, typ, arg):
    self.typ = typ
    self.arg = arg
  def __repr__(self):
    return "InjectFrom(%s, %s)" % (repr(self.typ), repr(self.arg))

class ProjectTo(Node):
  def __init__(self, typ, arg):
    self.typ = typ
    self.arg = arg
  def __repr__(self):
    return "ProjectTo(%s, %s)" % (repr(self.typ), repr(self.arg))

class Let(Node):
  def __init__(self, var, rhs, body):
    self.var = var
    self.rhs = rhs
    self.body = body
  def __repr__(self):
    return "Let(%s, %s, %s)" % (repr(self.var), repr(self.rhs), repr(self.body))

class IfStmt(Node):
  def __init__(self, then, test, else_):
     self.test  = test
     self.then  = then
     #self.then_bindings = then_bindings
     self.else_ = else_
     #self.else_bindings = else_bindings
  def __repr__(self):
     return "IfStmt(%s, %s, %s)" % \
             (repr(self.then), repr(self.test), repr(self.else_))

class IndirectCallFunc(Node):
	def __init__(self, func_ptr, free_vars, args):
		self.func_ptr = func_ptr
		self.free_vars = free_vars
		self.args = args
	def __repr__(self):
		return "IndirectCallFunc(%s, %s, %s)" % \
				(repr(self.func_ptr), repr(self.free_vars), repr(self.args))
# Create closure
class CreateClosure(Node):
  def __init__(self, name, argnames):
     self.name = name
     self.argnames = argnames
  def __repr__(self):
     return "CreateClosure(%s, %s)" % \
             (repr(self.name), repr(self.argnames))
