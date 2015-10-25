from compiler.ast import *
from explicate_ast import *


def assignment_site(instr):
	if isinstance(instr, Assign) and \
       isinstance(instr.nodes[0], AssName):
			return True
	return False

def local_vars1(n):
	print
	print "local vars1"
	print n
	print
	if isinstance(n, Lambda):
		lv = set([])
		# All lambda code is inside a Stmt node
		for instr in n.code.nodes:
			if assignment_site(instr):
				lv.add(instr.nodes[0].name)
		return lv - set(n.argnames)
