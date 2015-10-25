#!/usr/bin/python

from compiler import *
from explicate_ast import *
from freevars import *
#from closure_ast import *

TEMP_COUNT = 0
FUNC_COUNT = 0

def generate_func_name():
    global FUNC_COUNT
    variable_name = "func$_" + str(FUNC_COUNT)
    FUNC_COUNT = FUNC_COUNT + 1
    return variable_name

def generate_name(prefix):
	global TEMP_COUNT
	name = prefix + str(TEMP_COUNT)
	TEMP_COUNT += 1
	return name


def generate_let(node, args):
	name = Name(generate_name("indirect_tmp$"))
	return Let(name, node, IndirectCallFunc(CallFunc(Name('get_fun_ptr'), [name]), \
					CallFunc(Name('get_free_vars'), [name]), args))


def make_assign(lhs, rhs):
        return Assign([AssName(lhs, 'OP_ASSIGN')], rhs)


def create_closure(n):
	if isinstance(n, Stmt):
		nodes_res = [create_closure(n) for n in n.nodes]
		nodes = [n for (n, f) in nodes_res]
		func = reduce(lambda a, b: a + b, [f for (n, f) in nodes_res], [])
		return (Stmt(nodes), func)
	elif isinstance(n, Printnl):
		(node, function_defs) = create_closure(n.nodes[0])
		return (Printnl([node]), function_defs)
	elif isinstance(n, Assign):
		(e, function_defs) = create_closure(n.expr)
		n.expr = e
		return (n, function_defs)
	elif isinstance(n, Discard):
		(e, function_defs) = create_closure(n.expr)
		return (Discard(e), function_defs)
	elif isinstance(n, If):
		(test, func_defs_cond) = create_closure(n.tests[0][0])
		(then, func_defs_then) = create_closure(n.tests[0][1])
		(else_, func_defs_else) = create_closure(n.else_)
		tests = (test, then)
		return (If([tests], else_), func_defs_cond + func_defs_then + func_defs_else)
	elif isinstance(n, While):
		(n.test, func_defs_cond) = create_closure(n.test)
		(n.body, func_defs_body) = create_closure(n.body)
		return (n, func_defs_cond + func_defs_body)
	elif isinstance(n, Const):
		return (n, [])
	elif isinstance(n, Name):
		return (n, [])
	elif isinstance(n, AssName):
		return (n, [])
	elif isinstance(n, Add):
		(e1, function_defs1) = create_closure(n.left)
		(e2, function_defs2) = create_closure(n.right)
		return (Add((e1, e2)), function_defs1 + function_defs2)
	elif isinstance(n, UnarySub):
		(e, function_defs) = create_closure(n.expr)
		return (UnarySub(e), function_defs)
	elif isinstance(n, CallFunc):
		return (n, [])
	elif isinstance(n, IndirectCallFunc):
		(func_ptr, function_defs) = create_closure(n.func_ptr)
		# recurse over the args
		arg_results = [create_closure(arg) for arg in n.args]
		function_defs += reduce(lambda a, b: a + b, [f for (n, f) in arg_results], [])
		args = [a for (a, f) in arg_results]
		return (generate_let(func_ptr, args), function_defs)
	elif isinstance(n, Lambda):
		code, function_defs = create_closure(n.code)
		fvars = list(free_vars(n, set([])))

		free_vars_name = Name(generate_name("free_vars$"))
		free_vars_init = [make_assign(fvars[i], \
				 Subscript(free_vars_name, 'OP_APPLY', InjectFrom('INT', Const(i)))) \
				 for i in range(len(fvars))]
		new_code = free_vars_init + code.nodes
		func_name = generate_func_name()
		new_function = Lambda([free_vars_name] + n.argnames, func_name, n.flags, new_code)
		function_defs += [new_function]
		fvars = map(lambda a: Name(a), fvars)
		return (CreateClosure(func_name, List(fvars)), function_defs)
	elif isinstance(n, Return):
		(value, function_defs) = create_closure(n.value)
		return (Return(value), function_defs)
	elif isinstance(n, IfExp):
		(test, func_defs_test) = create_closure(n.test)
		(then, func_defs_then) = create_closure(n.then)
		(else_, func_defs_else) = create_closure(n.else_)
		return (IfExp(test, then, else_), \
				func_defs_test + func_defs_then + func_defs_else)
	elif isinstance(n, Compare):
		(e1, function_defs1) = create_closure(n.expr)
		(e2, function_defs2) = create_closure(n.ops[0][1])
		return (Compare(e1, [n.ops[0][0], e1]), function_defs1 + function_defs2)
	elif isinstance(n, Subscript):
		subs_res = [create_closure(s) for s in n.subs]
		subs = [s for (s, f) in subs_res]
		func = reduce(lambda a, b: a + b, [f for (s, f) in subs_res], [])
		(e, function_defs) = create_closure(n.expr)
		return (Subscript(e, n.flags, subs), function_defs + func)
	elif isinstance(n, List):
		nodes_res = [create_closure(node) for node in n.nodes]
		nodes = [n for (n, f) in nodes_res]
		function_defs = reduce(lambda a, b: a + b, [f for (n, f) in nodes_res], [])
		return (List(nodes), function_defs)
	elif isinstance(n, Dict):
		keys_res = [create_closure(k) for k in zip(*n.items)[0]]
		values_res = [create_closure(v) for v in zip(*n.items)[1]]
		keys = [k for (k, f) in keys_res]
		values = [v for (k, f) in values_res]
		keys_f = reduce(lambda a, b: a + b, [f for (k, f) in keys_res], [])
		values_f = reduce(lambda a, b: a + b, [f for (k, f) in values_res], [])
		return (Dict(zip(keys, values_res)), keys_f + values_f)
	elif isinstance(n, GetTag):
		return (n, [])
	elif isinstance(n, InjectFrom):
		return (n, [])
	elif isinstance(n, ProjectTo):
		return (n, [])
	elif isinstance(n, Let):
		(rhs, function_def_rhs) = create_closure(n.rhs)
		(body, function_def_body) = create_closure(n.body)
		return (Let(n.var, rhs, body), function_def_rhs + function_def_body)
	else:
		print
		print n
		raise Exception('Error in closure conversion: unrecognized AST node')

