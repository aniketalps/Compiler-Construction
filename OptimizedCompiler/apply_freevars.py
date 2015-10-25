#!/usr/bin/python

from compiler import *
from explicate_ast import *
from freevars import *

#mapping = []

def apply_free_vars(n, lambda_mapping):
	global mapping
	if isinstance(n, Module):
        	return apply_free_vars(n.node, lambda_mapping)
	elif isinstance(n, Stmt):
		fv_nodes = []
		for e in n.nodes:
			fv_nodes.append(apply_free_vars(e, lambda_mapping))
			#if isinstance(e, Lambda):
			#	lambda_mapping["lambda_"+str(e.argnames)] = mapping
        	return lambda_mapping
    	elif isinstance(n, Printnl):
		apply_free_vars(n.nodes[0], lambda_mapping)
		return lambda_mapping
    	elif isinstance(n, Assign):
		if isinstance(n.expr, list):
			[apply_free_vars(e, lambda_mapping) for e in n.expr]
		else:
			apply_free_vars(n.expr, lambda_mapping)
		for node in n.nodes:
			if isinstance(node, list):
				[apply_free_vars(e, lambda_mapping) for e in node]
			else:
				apply_free_vars(node, lambda_mapping)
		#Map free vars of each lambda to it
		#if isinstance(n.expr, Lambda):
		#	lambda_mapping[n.nodes[0].name] = mapping
		return lambda_mapping
    	elif isinstance(n, Discard):
		apply_free_vars(n.expr, lambda_mapping)
		return lambda_mapping
	elif isinstance(n, Const):
		return lambda_mapping
	elif isinstance(n, Name):
		if n.name not in lambda_mapping:
			print "n.name"
			print n.name
			lambda_mapping[n.name] = False
		return lambda_mapping
	elif isinstance(n, AssName):
		if n.name not in lambda_mapping:
			lambda_mapping[n.name] = False
		return lambda_mapping
	elif isinstance(n, Add):
		apply_free_vars(n.left, lambda_mapping)
		apply_free_vars(n.right, lambda_mapping)
		return lambda_mapping
	elif isinstance(n, UnarySub):
		apply_free_vars(n.expr, lambda_mapping)
		return lambda_mapping
	elif isinstance(n, CallFunc):
		[apply_free_vars(e, lambda_mapping) for e in n.args]
		return lambda_mapping
	elif isinstance(n, IndirectCallFunc):
		[apply_free_vars(e, lambda_mapping) for e in n.args]
		#free_in_args = reduce(lambda a, b: a | b, fv_args, set([]))
	        apply_free_vars(n.func_ptr, lambda_mapping)
		return lambda_mapping
	elif isinstance(n, Lambda):
		mapping = []
		for args in n.argnames:
			if args not in lambda_mapping:
				lambda_mapping[args] = False

		apply_free_vars(n.code, lambda_mapping)
		mapping = free_vars(n.code, set([])) - set(n.argnames)
		for freevar in mapping:
			lambda_mapping[freevar] = True
		return lambda_mapping
	elif isinstance(n, Return):
		apply_free_vars(n.value, lambda_mapping)
		return lambda_mapping
	elif isinstance(n, If):
		apply_free_vars(n.tests[0][0], lambda_mapping)
		apply_free_vars(n.tests[0][1], lambda_mapping)
		apply_free_vars(n.else_, lambda_mapping)
		return lambda_mapping
	elif isinstance(n, While):
		apply_free_vars(n.test, lambda_mapping)
		apply_free_vars(n.body, lambda_mapping)
		return lambda_mapping
	elif isinstance(n, IfExp):
		apply_free_vars(n.test, lambda_mapping)
		apply_free_vars(n.then, lambda_mapping)
		apply_free_vars(n.else_, lambda_mapping)
		return lambda_mapping
    	elif isinstance(n, Compare):
		apply_free_vars(n.expr, lambda_mapping)
		apply_free_vars(n.ops[0][1], lambda_mapping)
		return lambda_mapping
    	elif isinstance(n, Subscript):
		apply_free_vars(n.expr, lambda_mapping)
	        apply_free_vars(n.subs, lambda_mapping)
		return lambda_mapping
    	elif isinstance(n, List):
		[apply_free_vars(e, lambda_mapping) for e in n.nodes]
		return lambda_mapping
    	elif isinstance(n, Dict):
		[apply_free_vars(e[0], lambda_mapping) for e in n.items]
		[apply_free_vars(e[1], lambda_mapping) for e in n.items]
		return lambda_mapping
    	elif isinstance(n, And):
		apply_free_vars(n.nodes[0], lambda_mapping)
		apply_free_vars(n.nodes[1], lambda_mapping)
		return lambda_mapping
    	elif isinstance(n, Or):
		apply_free_vars(n.nodes[0], lambda_mapping)
		apply_free_vars(n.nodes[1], lambda_mapping)
		return lambda_mapping
    	elif isinstance(n, Not):
		apply_free_vars(n.expr, lambda_mapping)
		return lambda_mapping
	elif isinstance(n, GetTag):
		return lambda_mapping
        elif isinstance(n, InjectFrom):
		return lambda_mapping
        elif isinstance(n, ProjectTo):
		return lambda_mapping
        elif isinstance(n, Let):
		if n.var.name not in lambda_mapping:
			lambda_mapping[n.var.name] = False
		apply_free_vars(n.rhs, lambda_mapping)
		apply_free_vars(n.body, lambda_mapping)
		return lambda_mapping
	else:
		raise Exception('Error in apply_free_vars: unrecognized AST node')

