#!/usr/bin/python

import compiler
from compiler.ast import *
from compiler.transformer import *

unique_count = 0
scope_count = 0
#uniquify_flag = False

unique_table = {}

def uniquify_ast(n, uniquify_flag):
    global unique_count
    global scope_count
    #global uniquify_flag
    if isinstance(n, Module):
        return Module(None, uniquify_ast(n.node, uniquify_flag))
    elif isinstance(n, Stmt):
        uniquifyd_stmt = []
        for node in n.nodes:
            e = uniquify_ast(node, uniquify_flag)
            if isinstance(e, list):
                uniquifyd_stmt = uniquifyd_stmt + e
            else:
                uniquifyd_stmt.append(e)
        return Stmt(uniquifyd_stmt)
    elif isinstance(n, Printnl):
		e = uniquify_ast(n.nodes[0], uniquify_flag)
		return Printnl([e], None)
    elif isinstance(n, Assign):
		if isinstance(n.expr, list):
			expr = [uniquify_ast(e, uniquify_flag) for e in n.expr]
		else:
			expr = uniquify_ast(n.expr, uniquify_flag)
		for node in n.nodes:
			if isinstance(node, list):
				e = [uniquify_ast(e, uniquify_flag) for e in node]
			else:
				e = uniquify_ast(node, uniquify_flag)
		if not isinstance(e, list):
			e = [e]
		return Assign(e, expr)
    elif isinstance(n, Discard):
		e = uniquify_ast(n.expr, uniquify_flag)
		return e
    elif isinstance(n, If):
		test = uniquify_ast(n.tests[0][0], uniquify_flag)
		then = uniquify_ast(n.tests[0][1], uniquify_flag)
		else_ = uniquify_ast(n.else_, uniquify_flag)
		tests = (test, then)
		return If([tests], else_)
    elif isinstance(n, While):
	n.test = uniquify_ast(n.test, uniquify_flag)
	n.body = uniquify_ast(n.body, uniquify_flag)
	return n
    elif isinstance(n, AssName):
		if uniquify_flag == False:
			if str(n.name + "_" + str(scope_count)) not in unique_table.keys():
				unique_table[n.name+"_"+str(scope_count)] = unique_count
				unique_count += 1
		else:
			n.name = n.name + "_" + str(unique_table[n.name+"_"+str(scope_count)])
        	return [AssName(n.name,'OP_ASSIGN')]
    elif isinstance(n, Const):
		return n
    elif isinstance(n, Name):
		if uniquify_flag == True:
			if str(n.name + "_" + str(scope_count)) not in unique_table.keys():
				for key in unique_table.keys():
					if key.startswith(n.name+"_"):
						match = key
						n.name = n.name + "_" + str(unique_table[match])
			else:
				n.name = n.name + "_" + str(unique_table[n.name+"_"+str(scope_count)])
		return n
    elif isinstance(n, Add):
        n.left = uniquify_ast(n.left, uniquify_flag)
        n.right = uniquify_ast(n.right, uniquify_flag)
        return n
    elif isinstance(n, UnarySub):
        e = uniquify_ast(n.expr, uniquify_flag)
        return UnarySub(e)
    elif isinstance(n, CallFunc):
		uniq_args = []
		if n.args:
			for a in n.args:
				args = uniquify_ast(a, uniquify_flag)
				uniq_args.append(args)
		return CallFunc(uniquify_ast(n.node, uniquify_flag), uniq_args, None, None)
    elif isinstance(n, Function):
		code = []
		#argnames = []
		scope_count += 1
		if uniquify_flag == False:
			if n.name not in unique_table.keys():
				unique_table[n.name + "_" + str(scope_count)] = unique_count
				unique_count += 1
		else:
			n.name = n.name + "_" + str(unique_table[n.name+"_"+str(scope_count)])
		for argname in n.argnames:
			if uniquify_flag == False:
				if argname not in unique_table.keys():
					unique_table[argname + "_" + str(scope_count)] = unique_count
					unique_count += 1
		argnames = n.argnames
		
		if uniquify_flag == True:
			argnames = []
			for argname in n.argnames:
				if isinstance(argname, list):
				  for arg in argname:
					argnames.append(arg + "_" + str(unique_table[arg+"_"+str(scope_count)]))
				else:
					argnames.append(argname + "_" + str(unique_table[argname+"_"+str(scope_count)]))
			
		code = uniquify_ast(n.code, uniquify_flag)
		scope_count = scope_count - 1
		return Function(n.decorators, n.name, argnames, n.defaults, n.flags, n.doc, code)
    elif isinstance(n, Lambda):
		code = []
		scope_count += 1
		'''for argnames in n.argnames:
			if uniquify_flag == False:
				if argnames not in unique_table.keys():
					unique_table[argnames+"_"+str(scope_count)] = unique_count
					unique_count += 1
			else:
				argnames = argnames + "_" + str(unique_table[argnames+"_"+str(scope_count)])'''

		for argname in n.argnames:
			if uniquify_flag == False:
				if argname not in unique_table.keys():
					unique_table[argname + "_" + str(scope_count)] = unique_count
					unique_count += 1
		argnames = n.argnames
		
		if uniquify_flag == True:
			argnames = []
			for argname in n.argnames:
				if isinstance(argname, list):
				  for arg in argname:
					argnames.append(arg + "_" + str(unique_table[arg+"_"+str(scope_count)]))
				else:
				    if argname:
					argnames.append(argname + "_" + str(unique_table[argname+"_"+str(scope_count)]))
		print argnames
		code = uniquify_ast(n.code, uniquify_flag)
		scope_count -= 1
		return Lambda(argnames, n.defaults, n.flags, code)
    elif isinstance(n, Return):
		value = uniquify_ast(n.value, uniquify_flag)
		return Return(value)
    elif isinstance(n, IfExp):
		test = uniquify_ast(n.test, uniquify_flag)
		then = uniquify_ast(n.then, uniquify_flag)
		else_= uniquify_ast(n.else_, uniquify_flag)
		return IfExp(test,then,else_)
    elif isinstance(n, Compare):
		e = uniquify_ast(n.expr, uniquify_flag)
		ops = uniquify_ast(n.ops[0][1], uniquify_flag)
		return Compare(e, [(n.ops[0][0], ops)])
    elif isinstance(n, Subscript):
		e = uniquify_ast(n.expr, uniquify_flag)
	        subs = [uniquify_ast(x, uniquify_flag) for x in n.subs]
		return Subscript(e, n.flags, subs)
    elif isinstance(n, List):
		uniq_elements = []
		for expr in n.nodes:
			e = uniquify_ast(expr, uniquify_flag)
			uniq_elements.append(e)
		return List(uniq_elements)
    elif isinstance(n, Dict):
		uniq_items = []
		for item in n.items:
			key = uniquify_ast(item[0], uniquify_flag)
			val = uniquify_ast(item[1], uniquify_flag)
			uniq_items.append((key, val))
		return Dict(uniq_items)
    elif isinstance(n, And):
		return And([uniquify_ast(n.nodes[0], uniquify_flag), uniquify_ast(n.nodes[1], uniquify_flag)])
    elif isinstance(n, Or):
		return Or([uniquify_ast(n.nodes[0], uniquify_flag), uniquify_ast(n.nodes[1], uniquify_flag)])
    elif isinstance(n, Not):
		return Not(uniquify_ast(n.expr, uniquify_flag))
    else:
		print
		print n
		raise Exception('Error in uniquify_ast: unrecognized AST node')

def uniquify_pass(n):
	return uniquify_ast(uniquify_ast(n, False), True)
