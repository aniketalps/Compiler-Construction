#!/usr/bin/python

from compiler import *
#from compiler.ast import *
from explicate_ast import *
from local_vars1 import *


def free_vars_helper(n, previous_assigns):
	if isinstance(n, Module):
        	return free_vars_helper(n.node, previous_assigns)
	elif isinstance(n, Stmt):
		fv_nodes = []
		#fv_nodes = [free_vars_helper(e) for e in n.nodes]
		for e in n.nodes:
			#if isinstance(e, Lambda) or isinstance(e, Function) or isinstance(e, Assign):
			fv_nodes.append(free_vars_helper(e, previous_assigns))
		free_in_nodes = reduce(lambda a, b: a | b, fv_nodes, set([]))
        	return free_in_nodes - previous_assigns
    	elif isinstance(n, Printnl):
		e = free_vars_helper(n.nodes[0], previous_assigns)
		return e - previous_assigns
    	elif isinstance(n, Assign):
		free_expr = set([])
		free_nodes = set([])
		if isinstance(n.expr, list):
			fv_expr = [free_vars_helper(e, previous_assigns) for e in n.expr]
			free_expr = reduce(lambda a, b: a | b, fv_expr, set([]))
		else:
			free_expr = free_vars_helper(n.expr, previous_assigns)
		for node in n.nodes:
			if isinstance(node, list):
				e = [free_vars_helper(e, previous_assigns) for e in node]
				free_nodes = free_nodes | reduce(lambda a, b: a | b, e, set([]))
			else:
				free_nodes = free_vars_helper(node, previous_assigns)
		return (free_expr | free_nodes) - previous_assigns
    	elif isinstance(n, Discard):
		e = free_vars_helper(n.expr, previous_assigns)
		return e - previous_assigns
	elif isinstance(n, Const):
		return set([])
	elif isinstance(n, Name):
		if n.name == 'True' or n.name == 'False':
			return set([])
		else:
			print "n.name"
			print n.name
			return set([n.name]) - previous_assigns
	elif isinstance(n, AssName):
		if n.flags == "OP_APPLY":
			previous_assigns.add(n.name)
		return set([])
	elif isinstance(n, Add):
		return (free_vars_helper(n.left, previous_assigns) | free_vars_helper(n.right, previous_assigns)) - previous_assigns
	#	return set([])
	elif isinstance(n, UnarySub):
		return free_vars_helper(n.expr, previous_assigns) - previous_assigns
	elif isinstance(n, CallFunc):
		fv_args = [free_vars_helper(e, previous_assigns) for e in n.args]
		free_in_args = reduce(lambda a, b: a | b, fv_args, set([]))
		return (free_vars_helper(n.node, previous_assigns) | free_in_args) - previous_assigns
	elif isinstance(n, IndirectCallFunc):
		fv_args = [free_vars_helper(e, previous_assigns) for e in n.args]
		free_in_args = reduce(lambda a, b: a | b, fv_args, set([]))
		print "func_ptr"
		print n.func_ptr
		return (free_vars_helper(n.func_ptr, previous_assigns) | free_in_args) - previous_assigns
	elif isinstance(n, Lambda):
		#lv = local_vars1(n)
		#print
		return (free_vars_helper(n.code, previous_assigns) - set(n.argnames)) - previous_assigns
	elif isinstance(n, Return):
		return free_vars_helper(n.value, previous_assigns) - previous_assigns
	elif isinstance(n, IfExp):
		test = free_vars_helper(n.test, previous_assigns)
		then = free_vars_helper(n.then, previous_assigns)
		else_= free_vars_helper(n.else_, previous_assigns)
		return (test | then | else_) - previous_assigns
	elif isinstance(n, If):
		test = free_vars_helper(n.tests[0][0], previous_assigns)
		then = free_vars_helper(n.tests[0][1], previous_assigns)
		else_= free_vars_helper(n.else_, previous_assigns)
		return (test | then | else_) - previous_assigns
	elif isinstance(n, While):
		test = free_vars_helper(n.test, previous_assigns)
		body = free_vars_helper(n.body, previous_assigns)
		return (test | body) - previous_assigns
	elif isinstance(n, Compare):
		e = free_vars_helper(n.expr, previous_assigns)
		ops = free_vars_helper(n.ops[0][1], previous_assigns)
		return (e | ops) - previous_assigns
	elif isinstance(n, Subscript):
		if not isinstance(n.expr, Name):
			e = free_vars_helper(Name(n.expr), previous_assigns)
		else:
			e = free_vars_helper(n.expr, previous_assigns)
		subs = []
		for s in n.subs:
			if isinstance(s, Const):
				subs.append(free_vars_helper(s, previous_assigns))
			else:
				subs.append(free_vars_helper(Name(s), previous_assigns))
		return (e | reduce(lambda a, b: a | b, subs, set([]))) - previous_assigns
	elif isinstance(n, CreateClosure):
		if isinstance(n.name, Name):
			name = free_vars_helper(n.name, previous_assigns)
		else:
			name = free_vars_helper(Name(n.name), previous_assigns)
		
		argnames = [free_vars_helper(s, previous_assigns) for s in n.argnames]
		return (name | reduce(lambda a, b: a | b, argnames, set([]))) - previous_assigns
	elif isinstance(n, List):
		fv_expr = [free_vars_helper(e, previous_assigns) for e in n.nodes]
		free_in_expr = reduce(lambda a, b: a | b, fv_expr, set([]))
		return (free_in_expr) - previous_assigns
	elif isinstance(n, Dict):
		fv_items0 = [free_vars_helper(e[0], previous_assigns) for e in n.items]
		fv_items1 = [free_vars_helper(e[1], previous_assigns) for e in n.items]
		free_in_items = reduce(lambda a, b: a | b, fv_items0 + fv_items1, set([]))
		return free_in_items - previous_assigns
	elif isinstance(n, And):
		return (free_vars_helper(n.nodes[0], previous_assigns) | free_vars_helper(n.nodes[1], previous_assigns)) - previous_assigns
	elif isinstance(n, Or):
		return (free_vars_helper(n.nodes[0], previous_assigns) | free_vars_helper(n.nodes[1], previous_assigns)) - previous_assigns
	elif isinstance(n, Not):
		return (free_vars_helper(n.expr, previous_assigns)) - previous_assigns
	elif isinstance(n, GetTag):
		return set([])
		#return free_vars_helper(n.arg)
	elif isinstance(n, InjectFrom):
		#return free_vars_helper(n.arg)
		return set([])
	elif isinstance(n, ProjectTo):
		#return free_vars_helper(n.arg)
		return set([])
	elif isinstance(n, Let):
		#previous_assigns.add(n.var.name)
		print
		print "n.rhs"
		print n.rhs
		rhs = free_vars_helper(n.rhs, previous_assigns)
		body = free_vars_helper(n.body, previous_assigns)
		return (rhs | body) - previous_assigns - set([n.var.name])
	else:
		print n
		raise Exception('Error in free_vars_helper: unrecognized AST node')


def free_vars(n, previous_assigns):
	reserves = set(["print_any", "add", "error_pyobj"])
	fvars = free_vars_helper(n, previous_assigns)
	return fvars - reserves
