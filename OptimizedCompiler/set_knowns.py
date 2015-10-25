import compiler
from compiler.ast import *

def get_const_or_bool(node):
	if isinstance(node, Const):
		return node
	elif isinstance(node, Name):
		if node.name == "True" or node.name == "False":
			return node
	else:
		return None

def update_env(node):
	e = get_const_or_bool(node.expr)
	if e not None:
		if isinstance(node.nodes[0], AssName):
			environment[node.nodes[0].name] = e
		else:
			environment[node.subs[0].name] =			
		

def set_known_helper(n, environment):
    if isinstance(n, Module):
        return set_known_helper(n.node, environment)
    elif isinstance(n, Stmt):
        stmt = []
        for node in n.nodes:
            e = set_known_helper(node, environment)
            if isinstance(e, list):
                stmt = stmt + e
            else:
                stmt.append(e)
        return Stmt(stmt)
    elif isinstance(n, Printnl):
        n.nodes = [set_known_helper(n.nodes[0], environment)]
        return n
    elif isinstance(n, Assign):
		e = get_const_or_bool(n.expr)
		if
        n.nodes[0], environment)
        expr = set_known_helper(n.expr, environment)
        return Assign(n.nodes, expr)
    elif isinstance(n, AssName):
        return n
    elif isinstance(n, Discard):
        result = set_known_helper(n.expr, environment)
        return Discard(result)
    elif isinstance(n, Const):
        return n
    elif isinstance(n, Name):
        return n
    elif isinstance(n, Add):
		n.left = set_known_helper(n.left, environment)
		n.right = set_known_helper(n.right, environment)
        return compress(n)
    elif isinstance(n, UnarySub):
		n.expr = set_known_helper(n.expr, environment)
		return n
    elif isinstance(n, Function):
		return n
    elif isinstance(n, Lambda):
	return n
    elif isinstance(n, Return):
		value = set_known_helper(n.value, environment)
		return Return(value)
    elif isinstance(n, CallFunc):
		return n
    elif isinstance(n, Compare):  #new
        e1 = set_known_helper(n.expr, environment)
        e2 = set_known_helper(n.ops[0][1], environment)
        return Compare(e1, [n.ops[0][0], e1])
    elif isinstance(n, And):      #new
        n.nodes[0] = set_known_helper(n.nodes[0], environment)
        n.nodes[1] = set_known_helper(n.nodes[1], environment)
        return n
    elif isinstance(n, Or):       #new
        n.nodes[0] = set_known_helper(n.nodes[0], environment)
        n.nodes[1] = set_known_helper(n.nodes[1], environment)
        return n
    elif isinstance(n, Not):      #new
        n.expr = set_known_helper(n.expr, environment)
        return n
    elif isinstance(n, List):     #new
        e = []
        for n in n.nodes:
            e.append(set_known_helper(n), environment)
        return List(e)
    elif isinstance(n, Dict):     #new
        exp_items = []
        for n in n.items:
            key = set_known_helper(n[0], environment)
            val = set_known_helper(n[1], environment)
            exp_items.append((key, val))
        return Dict(exp_items)
    elif isinstance(n, Subscript):     #new
		n.expr =  set_known_helper(n.expr, environment)
		n.subs[0] = set_known_helper(n.subs[0], environment)
		return n
    elif isinstance(n, If):
		n.tests[0][0] = set_known_helper(n.tests[0][0], environment)
		n.test[0][1] = set_known_helper(n.tests[0][1], environment)
		n.else_ = set_known_helper(n.else_, environment)
		return n
    elif isinstance(n, While):
		n.test = set_known_helper(n.test, environment)
		n.body = set_known_helper(n.body, environment)
		return n
    elif isinstance(n, IfExp):
        n.test = set_known_helper(n.test, environment)
        n.then = set_known_helper(n.then, environment)
        n.else_= set_known_helper(n.else_, environment)
        return n
    else:
        print "Error"
        print n
        raise Exception('Error in set_known_helper: unrecognized AST node')


def set_knowns(ast):
	return set_known_helper(ast, environment)


ast = compiler.parse('m = 1 + 2 + -3; print m; m = 9+10+10')
print compress_add(ast)
