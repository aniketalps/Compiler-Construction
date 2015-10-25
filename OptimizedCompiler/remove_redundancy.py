#!/usr/bin/python

import compiler
from x86_ast import *
from compiler.ast import *
from explicate_ast import *


def remove_red(x86):
	new_86 = []
	for inst in x86:
		if (isinstance(inst, Movl) and isinstance(inst.left, Name) \
		and isinstance(inst.right, Name) and \
		inst.left.name != inst.right.name):
			`new_86.append(inst)
		else:
			new_86.append(inst)
	return new_86
