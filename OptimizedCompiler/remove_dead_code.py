import compiler
from compiler.ast import *


def handle_const(node):
		if node.value:
			return True
		else:
			return False

def handle_name(node):
		if (node.name == "True" or node.name == "False"):
			if node.name == "True":
				return True
			return False
		return None

call = {'==': lambda a, b: a == b, '!=': lambda a, b: a != b}
def handle_two_const(op, e1, e2):
	return call[op](e1, e2)

def handle_name_const(op, e1, e2):
		name_result = handle_name(e1)
		return call[op](name_result, e1) if name_result is not None else None

def handle_const_name(op, e1, e2):
	name_result = handle_name(e2)
	return call[op](name_result, e2) if (name_result is not None) else None

def handle_two_names(op, e1, e2):
	if e1.name == e2.name:
		return True
	name_result1 = handle_name(e1)
	name_result2 = handle_name(e2)
	return call[op](name_result1, name_result2) if ((name_result1 is not None) and (name_result2 is not None)) else None


def handle_compare(node):
	if isinstance(node.expr, Const) and isinstance(node.ops[1], Const):
		return handle_two_const(node.ops[0], node.expr.value, node.ops[1].value)
	if isinstance(node.expr, Name) and isinstance(node.ops[0][1], Const):
		return handle_name_const(node.ops[0], node_expr, node.ops[1].value)
	if isinstance(node.ops[1], Name) and isinstance(node.expr, Const):
		return handle_name_const(node.ops[0], node.ops[1], node.expr)
	if isinstance(node.ops[1], Name) and isinstance(node.expr, Name):
		return handle_two_names(node.ops[0], node.ops[1], node.expr)
	return None
	

def examine_test(condition):
	if isinstance(condition, Const):
		return handle_const(condition)
	elif isinstance(condition, Name):
		return handle_name(condition)
	elif isinstance(condition, Compare):
		return handle_compare(condition)


def handle_while(n):
	result = examine_test(n.test)
	if not result:
		return Discard(Const(0))
	else:
		return n

def handle_if(n):
	result = examine_test(n.tests[0][0])
	if result:
		return n.tests[0][1]
	elif result is None:
		return n
	else:
		return n.else_

def handle_ifExp(n):
	result = examine_test(n.test)
	if result:
		return n.then
	elif result is None:
		return n
	else:
		return n.else_

def dead_helper(n):
    if isinstance(n, Module):
        return dead_helper(n.node)
    elif isinstance(n, Stmt):
        stmt = []
        for node in n.nodes:
            e = dead_helper(node)
            if isinstance(e, list):
                stmt = stmt + e
            elif isinstance(e, Stmt):
                stmt = stmt + [node for node in e.nodes]
            else:
                stmt.append(e)
        return Stmt(stmt)
    elif isinstance(n, Printnl):
        n.nodes = [dead_helper(n.nodes[0])]
        return n
    elif isinstance(n, Assign):
        nodes = dead_helper(n.nodes[0])
        expr = dead_helper(n.expr)
        return Assign(n.nodes, expr)
    elif isinstance(n, AssName):
        return n
    elif isinstance(n, Discard):
        result = dead_helper(n.expr)
        return Discard(result)
    elif isinstance(n, Const):
        return n
    elif isinstance(n, Name):
        return n
    elif isinstance(n, Add):
		n.left = dead_helper(n.left)
		n.right = dead_helper(n.right)
		return n
    elif isinstance(n, UnarySub):
		n.expr = dead_helper(n.expr)
		return n
    elif isinstance(n, Function):
		return n
    elif isinstance(n, Lambda):
	return n
    elif isinstance(n, Return):
		value = dead_helper(n.value)
		return Return(value)
    elif isinstance(n, CallFunc):
		return n
    elif isinstance(n, Compare):  #new
        e1 = dead_helper(n.expr)
        e2 = dead_helper(n.ops[0][1])
        return Compare(e1, [n.ops[0][0], e1])
    elif isinstance(n, And):      #new
        n.nodes[0] = dead_helper(n.nodes[0])
        n.nodes[1] = dead_helper(n.nodes[1])
        return n
    elif isinstance(n, Or):       #new
        n.nodes[0] = dead_helper(n.nodes[0])
        n.nodes[1] = dead_helper(n.nodes[1])
        return n
    elif isinstance(n, Not):      #new
        n.expr = dead_helper(n.expr)
        return n
    elif isinstance(n, List):     #new
        e = []
        for n in n.nodes:
            e.append(dead_helper(n))
        return List(e)
    elif isinstance(n, Dict):     #new
        exp_items = []
        for n in n.items:
            key = dead_helper(n[0])
            val = dead_helper(n[1])
            exp_items.append((key, val))
        return Dict(exp_items)
    elif isinstance(n, Subscript):     #new
		n.expr =  dead_helper(n.expr)
		n.subs[0] = dead_helper(n.subs[0])
		return n
    elif isinstance(n, If):
		print
		print "If"
		print n.tests[0][0]
		print n.tests[0][1]
		print
		n.tests[0] = (dead_helper(n.tests[0][0]), dead_helper(n.tests[0][1]))
		n.else_ = dead_helper(n.else_)
		return handle_if(n)
    elif isinstance(n, While):
		n.test = dead_helper(n.test)
		n.body = dead_helper(n.body)
		return handle_while(n)
    elif isinstance(n, IfExp):
		n.then = dead_helper(n.then)
		n.test = dead_helper(n.test)
		n.else_ = dead_helper(n.else_)
		return handle_ifExp(n)
    else:
        print "Error"
        print n
        raise Exception('Error in dead_helper: unrecognized AST node')


def compress_dead_code(ast):
	return dead_helper(ast)


#ast = compiler.parse('42 if 1 and 0 else 1')
#print ast
#print compress_dead_code(ast)

