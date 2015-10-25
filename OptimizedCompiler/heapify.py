#!/usr/bin/python

from compiler import *
from explicate_ast import *

COUNT = 0
def make_name():
	global COUNT
	var = "heapify$_" + str(COUNT)
	COUNT += 1
	return var

def params_assign(allocs, params, lambda_mapping):
	copy = allocs[:]
	assigns = []
	for param in params:
		if "heapify$" in param:
			assigns.append(Assign([Subscript(Name(copy[0].nodes[0].name), 'OP_ASSIGN', \
			[Const(0)])], Name(param)))
			del copy[0]
	return assigns

def do_nothing(node):
	if isinstance(node, Const) or \
       isinstance(node, GetTag) or \
       isinstance(node, ProjectTo) or \
       isinstance(node, AssName) or\
       isinstance(node, InjectFrom):
		return True
	else:
		return False

def heapify(n, lambda_mapping, assign_dict):
	if isinstance(n, Stmt):
		heapified_stmt = []
		for node in n.nodes:
			h = heapify(node, lambda_mapping, assign_dict)
			if isinstance(h, list):
				heapified_stmt = heapified_stmt + h
			else:
				heapified_stmt.append(h)
		return Stmt(heapified_stmt)
	elif isinstance(n, Printnl):
		n.nodes[0] = heapify(n.nodes[0], lambda_mapping, assign_dict)
		return n
	elif isinstance(n, Assign):
		if lambda_mapping[n.nodes[0].name]:
			print
			print "ASSIGN HEAP"
			print n.nodes
			print
			rhs = heapify(n.expr, lambda_mapping, assign_dict)
			create_list = [Assign([AssName(n.nodes[0].name, 'OP_ASSIGN')], List([InjectFrom('INT', Const(0))]))]
			return create_list + [Assign([Subscript(Name(n.nodes[0].name), 'OP_ASSIGN', [Const(0)])], rhs)]
		elif isinstance(n.expr, Lambda):
			new_code = heapify(n.expr, lambda_mapping, assign_dict)
			n.expr.code = new_code
			#new_lambda = heapify(n.expr, lambda_mapping, assign_dict)
		return n
	elif isinstance(n, Discard):
		n.expr = heapify(n.expr, lambda_mapping, assign_dict)
		return n
	elif isinstance(n, If):
		test = heapify(n.tests[0][0], lambda_mapping, assign_dict)
		then = heapify(n.tests[0][1], lambda_mapping, assign_dict)
		else_ = heapify(n.else_, lambda_mapping, assign_dict)
		tests = (test, then)
		return If([tests], else_)
	elif isinstance(n, While):
		n.test = heapify(n.test, lambda_mapping, assign_dict)
		n.body = heapify(n.body, lambda_mapping, assign_dict)
		return n
	elif isinstance(n, Name):
		if lambda_mapping[n.name] == True:
			n = Subscript(Name(n.name), 'OP_APPLY', [Const(0)])
		return n
	elif isinstance(n, Add):
		n.left = heapify(n.left, lambda_mapping, assign_dict)
		n.right = heapify(n.right, lambda_mapping, assign_dict)
		return n
	elif isinstance(n, UnarySub):
		n.expr = heapify(n.expr, lambda_mapping, assign_dict)
		return n
	elif isinstance(n, CallFunc):
		n.args = [heapify(e, lambda_mapping, assign_dict) for e in n.args]
		return n
	elif isinstance(n, IndirectCallFunc):
		n.func_ptr = heapify(n.func_ptr, lambda_mapping, assign_dict)
		n.args = [heapify(e, lambda_mapping, assign_dict) for e in n.args]
		return n
	elif isinstance(n, Lambda):
		print n
		params_alloc = [Assign([AssName(arg, 'OP_ASSIGN')], List([InjectFrom("INT", Const(0))])) \
			for arg in n.argnames if lambda_mapping[arg]]
		argnames = [make_name() if lambda_mapping[arg] else arg for arg in n.argnames]
		params_init = params_assign(params_alloc, argnames, lambda_mapping)
		new_code = heapify(n.code, lambda_mapping, assign_dict)
		return Lambda(argnames, n.defaults, n.flags, Stmt(params_alloc + params_init + new_code.nodes))
	elif isinstance(n, Return):
		n.value = heapify(n.value, lambda_mapping, assign_dict)
		return n
	elif isinstance(n, IfExp):
		n.test = heapify(n.test, lambda_mapping, assign_dict)
		n.then = heapify(n.then, lambda_mapping, assign_dict)
		n.else_ = heapify(n.else_, lambda_mapping, assign_dict)
		return n
	elif isinstance(n, Compare):
		n.expr = heapify(n.expr, lambda_mapping, assign_dict)
		n.ops[0][1] = heapify(n.ops[0][1], lambda_mapping, assign_dict)
		return n
	elif isinstance(n, Subscript):
		n.expr = heapify(n.expr, lambda_mapping, assign_dict)
		n.subs = heapify(n.subs, lambda_mapping, assign_dict)
		return n
	elif isinstance(n, List):
		n.nodes = [heapify(e, lambda_mapping, assign_dict) for e in n.nodes]
		return n
	elif isinstance(n, Dict):
		n.items = [heapify(e[0], lambda_mapping, assign_dict) for e in n.items]
		n.items = [heapify(e[1], lambda_mapping, assign_dict) for e in n.items]
		return n
	elif isinstance(n, And):
		n.nodes[0] = heapify(n.nodes[0], lambda_mapping, assign_dict)
		n.nodes[1] = heapify(n.nodes[1], lambda_mapping, assign_dict)
		return n
	elif isinstance(n, Or):
		n.nodes[0] = heapify(n.nodes[0], lambda_mapping, assign_dict)
		n.nodes[1] = heapify(n.nodes[1], lambda_mapping, assign_dict)
		return n
	elif isinstance(n, Not):
		n.expr = heapify(n.expr, lambda_mapping, assign_dict)
		return n
	elif isinstance(n, Let):
		rhs = heapify(n.rhs, lambda_mapping, assign_dict)
		n.rhs = rhs
		n.body = heapify(n.body, lambda_mapping, assign_dict)
		return n
	elif do_nothing(n):
		return n
	else:
		raise Exception('Error in heapify: unrecognized AST node')

def heapify_ast(n, lambda_mapping):
	assign_dict = lambda_mapping.copy()
	heap_dict = heapify(n, lambda_mapping, assign_dict)
	print
	print "Heap dict"
	print lambda_mapping
	print
	return heap_dict
