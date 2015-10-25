#!/usr/bin/python

from compiler import *
from explicate_ast import *

def local_interpreter(n, local_env):
	if isinstance(n, Module):
		return Module(n.doc, local_interpreter(n.node, local_env))
	elif isinstance(n, Stmt):
        	stmt = []
        	for node in n.nodes:
            		e = local_interpreter(node, local_env)
            		if isinstance(e, list):
                		stmt = stmt + e
            		else:
                		stmt.append(e)
        	return Stmt(stmt)
	elif isinstance(n, Printnl):
		n.nodes[0] = local_interpreter(n.nodes[0], local_env)
		return n
	elif isinstance(n, CallFunc):
		expr_args = []
		for a in n.args:
			expr_args.append(local_interpreter(a, local_env))
		return CallFunc(n.node, expr_args, None, None)
	elif isinstance(n, Assign):
		n.nodes[0] = local_interpreter(n.nodes[0], local_env)
		n.expr = local_interpreter(n.expr, local_env)
		if isinstance(n.nodes[0], AssName) and (isinstance(n.expr, Const)):
			local_env[n.nodes[0].name] = n.expr
		return n
	elif isinstance(n, Discard):
		expr = local_interpreter(n.expr, local_env)
		return Discard(expr)
	elif isinstance(n, Return):
		return Return(local_interpreter(n.value, local_env))
	elif isinstance(n, Let):
		return Let(n.var, local_interpreter(n.rhs, local_env), local_interpreter(n.body, local_env))
	elif isinstance(n, If):
		then = [] #[translate_worker([inst]) for inst in s.then]
		else_ = [] #[translate_worker([inst]) for inst in s.else_]
		test = []
		then = [local_interpreter(inst, local_env) for inst in n.then]
		else_ = [local_interpreter(inst, local_env) for inst in n.else_]
		return If(local_interpreter(n.test, local_env), Stmt(then, local_env), Stmt(else_, local_env))
	elif isinstance(n, While):
		n.body = Stmt(local_interpreter(n.body, local_env))
		n.test = local_interpreter(n.test)
		return n
	elif isinstance(n, Lambda):
		n.argnames = [local_interpreter(arg, local_env) for arg in n.argnames]
		n.code = local_interpreter(n.code, local_env)
		return n
    	elif isinstance(n, AssName):
        	return n
    	elif isinstance(n, Const):
		return n
    	elif isinstance(n, Name):
		if n.name in local_env.keys():
			return local_env[n.name]
		return n
    	elif isinstance(n, Add):
		n.left = local_interpreter(n.left, local_env)
		n.right = local_interpreter(n.right, local_env)
		return n
    	elif isinstance(n, UnarySub):
		n.expr = local_interpreter(n.expr, local_env)
        	return n
    	elif isinstance(n, IfExp):
		n.test = local_interpreter(n.test, local_env)
		n.then = local_interpreter(n.then, local_env)
		n.else_ = local_interpreter(n.else_, local_env)
		return n
    	elif isinstance(n, Compare):
		(atomic_l, bindings_l) = local_interpreter(n.expr, local_env)
		(atomic_r, bindings_r) = local_interpreter(n.ops[0][1], local_env)
		return Compare(local_interpreter(n.expr, local_env), [n.ops[0][0], local_interpreter(n.ops[0][1], local_env)])
    	elif isinstance(n, Subscript):
		return Subscript(local_interpreter(n.expr, local_env), [n.subs[0], local_interpreter(n.subs[1], local_env)])
    	elif isinstance(n, List):
		return List([local_interpreter(i, local_env) for i in n.nodes])
    	elif isinstance(n, Dict):
		return Dict([(local_interpreter(k, local_env), local_interpreter(v, local_env)) for k,v in n.items])
	elif isinstance(n, And): 
		return And([local_interpreter(node) for node in n.nodes])
	elif isinstance(n, Or): 
		return Or([local_interpreter(node) for node in n.nodes])
	elif isinstace(n, Not):
		return Not(local_interpreter(n.expr))
    	else:
		print
		print n
		print
		raise Exception('Error in local_interpreter: unrecognized AST node')

if __name__ == "__main__":
	from compiler import *
	ast = parse('x = 3\ny = 55\ny = y + x + 4\nz = x + y + 5')
	print ast
	print local_interpreter(ast, {})
