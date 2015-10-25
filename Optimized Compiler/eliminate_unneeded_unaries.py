import compiler
from compiler.ast import *


def compress_fold(node, is_neg):
	if not isinstance(node, UnarySub):
		if is_neg:
			return UnarySub(node)
		return node

	return compress_fold(node.expr, not is_neg)

def remove_helper(n):
    if isinstance(n, Module):
        return remove_helper(n.node)
    elif isinstance(n, Stmt):
        stmt = []
        for node in n.nodes:
            e = remove_helper(node)
            if isinstance(e, list):
                stmt = stmt + e
            else:
                stmt.append(e)
        return Stmt(stmt)
    elif isinstance(n, Printnl):
        n.nodes = [remove_helper(n.nodes[0])]
        return n
    elif isinstance(n, Assign):
        nodes = remove_helper(n.nodes[0])
        expr = remove_helper(n.expr)
        return Assign(n.nodes, expr)
    elif isinstance(n, AssName):
        return n
    elif isinstance(n, Discard):
        result = remove_helper(n.expr)
        return Discard(result)
    elif isinstance(n, Const):
        return n
    elif isinstance(n, Name):
        return n
    elif isinstance(n, Add):
        res_l = remove_helper(n.left)
        res_r = remove_helper(n.right)
        return Add((res_l, res_r))
    elif isinstance(n, UnarySub):
		temp = compress_fold(n, False)
		print temp
		return temp
    elif isinstance(n, Function):
		return n
    elif isinstance(n, Lambda):
	return n
    elif isinstance(n, Return):
		value = remove_helper(n.value)
		return Return(value)
    elif isinstance(n, CallFunc):
		return n
    elif isinstance(n, Compare):  #new
        e1 = remove_helper(n.expr)
        e2 = remove_helper(n.ops[0][1])
        return Compare(e1, [n.ops[0][0], e1])
    elif isinstance(n, And):      #new
        n.nodes[0] = remove_helper(n.nodes[0])
        n.nodes[1] = remove_helper(n.nodes[1])
        return n
    elif isinstance(n, Or):       #new
        n.nodes[0] = remove_helper(n.nodes[0])
        n.nodes[1] = remove_helper(n.nodes[1])
        return n
    elif isinstance(n, Not):      #new
        n.expr = remove_helper(n.expr)
        return n
    elif isinstance(n, List):     #new
        e = []
        for n in n.nodes:
            e.append(remove_helper(n))
        return List(e)
    elif isinstance(n, Dict):     #new
        exp_items = []
        for n in n.items:
            key = remove_helper(n[0])
            val = remove_helper(n[1])
            exp_items.append((key, val))
        return Dict(exp_items)
    elif isinstance(n, Subscript):     #new
        explicated_expr =  remove_helper(n.expr)
        explicated_sub  = remove_helper(n.subs[0])
        return Subscript(explicated_expr, n.flags, explicated_sub)
    elif isinstance(n, If):
		print
		print n.tests[0][0]
		print 
		print n.tests[0][1]
		n.tests[0] = (remove_helper(n.tests[0][0]), remove_helper(n.tests[0][1]))
		n.else_ = remove_helper(n.else_)
		return n
    elif isinstance(n, While):
		n.test = remove_helper(n.test)
		n.body = remove_helper(n.body)
		return n
    elif isinstance(n, IfExp):
        n.test = remove_helper(n.test)
        n.then = remove_helper(n.then)
        n.else_= remove_helper(n.else_)
        return n
    else:
        print "Error"
        print n
        raise Exception('Error in remove_helper: unrecognized AST node')


def remove_unneeded_unaries(ast):
	return remove_helper(ast)


#ast = compiler.parse('--input()')
#print
#print ast
#print
#print remove_unneeded_unaries(ast)

