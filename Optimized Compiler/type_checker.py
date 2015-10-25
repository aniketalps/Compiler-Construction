#!/usr/bin/python

from explicate_ast import *
from compiler.ast import *

TYPES = ['INT', 'BOOL', 'BIGPYOBJ', 'PYOBJ']

def ERROR(s, node):
	print s
	print node

def type_check(environment, e):
	if isinstance(e, Const):
		return 'INT'
	elif isinstance(e, Name):
		if (e.name in ['True', 'False']):
			return 'BOOL'
		return environment(e.name)
	elif isinstance(e, InjectFrom):
		if (type_check(environment, e.arg) == e.typ):
			return 'PYOBJ'
		else:
			ERROR("InjectFrom node failed to type_check", e)
	elif isinstance(e, ProjectTo):
		if (type_check(environment, e.arg) == 'PYOBJ'):
			return e.typ
		else:
			ERROR("ProjectTo node failed to type_check", e)
	elif isinstance(e, UnarySub):
		if (type_check(environment, e.expr) == 'INT'):
			return 'INT'
		else:
			ERROR("UnarySub node failed to type_check", e)
	elif isinstance(e, GetTag):
		if (type_check(environment, e.expr) == 'PYOBJ'):
			return 'INT'
		else:
			ERROR("GetTag node failed to type_check", e)
	elif isinstance(e, Compare):
		if (type_check(environment, e.expr) == 'PYOBJ'):
			return 'INT'
		else:
			ERROR("GetTag node failed to type_check", e)


c = Const(1)
b = Name("True")
i = InjectFrom("INT", c)
i2 = InjectFrom("INT", b)

type_check({}, c)
type_check({}, b)
type_check({}, i)
type_check({}, i2)
