#!/usr/bin/python

from compiler import *
from explicate_ast import *

depth_count = 0
local_count = 0
PASS = False
FLAG = 0
add_list = []

def constant_folding_pass(n):
	global local_count
	global depth_count
	global PASS
	global FLAG
	global add_list
	if isinstance(n, Module):
		return Module(n.doc, constant_folding_pass(n.node))
	elif isinstance(n, Stmt):
        	stmt = []
        	for node in n.nodes:
            		e = constant_folding_pass(node)
            	if isinstance(e, list):
                	stmt = stmt + e
            	else:
                	stmt.append(e)
        	return Stmt(stmt)
	elif isinstance(n, Printnl):
		n.nodes = [constant_folding_pass(n.nodes[0])]
		return n
	elif isinstance(n, CallFunc):
		expr_args = []
		for a in n.args:
			expr_args.append(constant_folding_pass(a))
		return CallFunc(n.node, expr_args, None. None)
	elif isinstance(n, Assign):
		nodes = constant_folding_pass(n.nodes[0])
		expr = constant_folding_pass(n.expr)
		return Assign(nodes, expr)
	elif isinstance(n, Discard):
		return Discard(constant_folding_pass(n.expr))
	elif isinstance(n, Return):
		return Return(constant_folding_pass(n.value))
	elif isinstance(n, Let):
		return Let(n.var, constant_folding_pass(n.rhs), constant_folding_pass(n.body))
	elif isinstance(n, If):
		then = [] #[translate_worker([inst]) for inst in s.then]
		else_ = [] #[translate_worker([inst]) for inst in s.else_]
		test = []
		for inst in n.then:
			then = then + constant_folding_pass(inst)
		for inst in n.else_:
			else_ = else_ + constant_folding_pass(inst)
		return If(constant_folding_pass(n.test), Stmt(then), Stmt(else_))
	elif isinstance(n, While):
		n.body = Stmt(constant_folding_pass(n.body))
		n.test = constant_folding_pass(n.test)
		return n
	elif isinstance(n, Lambda):
		n.argnames = [constant_folding_pass(arg) for arg in n.argnames]
		n.code = constant_folding_pass(n.code)
		return n
    	elif isinstance(n, AssName):
        	return n
    	elif isinstance(n, Const):
		return n
    	elif isinstance(n, Name):
		return n
    	elif isinstance(n, Add):
		if PASS == True:
			n.left = constant_folding_pass(n.left)
			if not isinstance(n.left, Add):
				add_list.append(n.left)
			n.right = constant_folding_pass(n.right)
			if not isinstance(n.right, Add):
				add_list.append(n.right)
			depth_count += 1
		else:
			local_count += 1
			if local_count == depth_count:
				if FLAG == 0:
					local_count = 0
					FLAG = 1

			n.left = constant_folding_pass(n.left)
			depth_count = depth_count - 1
			n.right = constant_folding_pass(n.right)
			if FLAG == 1 and depth_count == 0:
				n = make_add()
				return n
		return n
    	elif isinstance(n, UnarySub):
        	return n
    	elif isinstance(n, IndirectCallFunc):
		expr_args = []
		for a in n.args:
			if not isinstance(a, Name):
				a = Name(a)
			expr_args.append(constant_folding_pass(a))
		return IndirectCallFunc(expr.func_ptr, expr.free_vars, expr_args)
    	elif isinstance(n, CreateClosure):
		expr_args = []
		for a in n.argnames:
			expr_args.append(constant_folding_pass(a))
		return CreateClosure(n.name, expr_args)
    	elif isinstance(n, IfExp):
		n.test = constant_folding_pass(n.test)
		n.then = constant_folding_pass(n.then)
		n.else_ = constant_folding_pass(n.else_)
		return n
    	elif isinstance(n, Compare):
		(atomic_l, bindings_l) = flatten_expr(n.expr)
		(atomic_r, bindings_r) = flatten_expr(n.ops[0][1])
		return Compare(constant_folding_pass(n.expr), [n.ops[0][0], constant_folding_pass_n.ops[0][1]])
    	elif isinstance(n, Subscript):
		return Subscript(constant_folding_pass(n.expr, [n.subs[0], constant_folding_pass(n.subs[1])]))
    	elif isinstance(n, GetTag):
		return GetTag(n.typ, constant_folding_pass(n.arg))
    	elif isinstance(n, InjectFrom):
		return InjectFrom(n.typ, constant_folding_pass(n.arg))
    	elif isinstance(n, ProjectTo):
		return ProjectTo(n.typ, constant_folding_pass(n.arg))
    	elif isinstance(n, List):
		return List([constant_folding_pass(i) for i in n.nodes])
    	elif isinstance(n, Dict):
		return Dict([(constant_folding_pass(k), constant_folding_pass(v)) for k,v in n.items])
    	else:
		print
		print n
		print
		raise Exception('Error in constant_folding_pass: unrecognized AST node')

def make_add():
	global add_list
	index_arr = 0
	val = 0
	namelist = []
	for const in add_list:
		print const
		if isinstance(const, Const):
			val += const.value
	for elements in add_list:
		if isinstance(elements, Name):
			namelist.append(elements)
	if namelist:
		for i in range(0,len(namelist)):
			if i == 0:
				n = Add(Const(val), namelist[i])
			else:
				n = Add(namelist[i], n)
	else:
		n = Const(val)
	print n
	return n

def constant_folding(n):
	global depth_count
	global PASS
	depth_count = 0
	PASS = True
	constant_folding_pass(n)
	PASS = False
	ast = constant_folding_pass(n)
	return ast


if __name__ == "__main__":
	import compiler
	ast = compiler.parse('x = 1+3+4; print x; x = 5+5')
	print ast
	print constant_folding(ast)
