import compiler
from compiler.ast import *
import sys, os

def mapreduce(n1, n2):
	if len(n1) == len(n2):
		values = [dispatch(n1, n2) for (n1, n2) in zip(n1,n2)]
		return reduce(lambda a ,b: a and b, values, True)
	return False

def get_class_name(n):
	return n.__class__.__name__

def dispatch(n1, n2):
		klass1 = get_class_name(n1)
		klass2 = get_class_name(n2)
		return HANDLERS[klass1](n1, n2) if klass1 == klass2 else False

def handle_printnl(n1, n2):
		return dispatch(n1.nodes[0], n2.nodes[0])

def handle_assign(n1, n2):
		return dispatch(n1.nodes[0], n2.nodes[0])  \
			   and dispatch(n1.expr, n2.expr)

def handle_assname(n1, n2):
        return (n1.name == n2.name) \
			   and (n1.flags == n2.flags)

def handle_discard(n1, n2):
		return dispatch(n1.expr, n2.expr)

def handle_const(n1, n2):
        return n1.value == n2.value

def handle_name(n1, n2):
		return n1.name == n2.name

def handle_add(n1, n2):
		return dispatch(n1.left, n2.left)  \
			   and dispatch(n1.right, n2.right)

def handle_unarysub(n1, n2):
		return dispatch(n1.expr, n2.expr)

def handle_function(n1, n2):
		return n

def handle_lambda(n1, n2):
	return n

def handle_return(n1, n2):
		return dispatch(n1.value, n2.value)

def handle_callfunc(n1, n2):
		print n1.node
		return dispatch(n1.node, n2.node)

def handle_compare(n1, n2):
		return dispatch(n1.ops[0][1], n2.ops[0][1]) \
			   and dispatch(n1.expr, n2.expr) \
			   and n1.ops[0][0] == n2.ops[0][0]

def handle_and(n1, n2):
		return dispatch(n1.nodes[0], n2.nodes[0]) \
			   and dispatch(n1.nodes[1], n2.nodes[1])

def handle_or(n1, n2):
		return dispatch(n1.nodes[0], n2.nodes[0]) \
			   and dispatch(n1.nodes[1], n2.nodes[1])

def handle_not(n1, n2):
        return dispatch(n1.expr, n2.expr)

def handle_list(n1, n2):
		return mapreduce(n1.nodes, n2.nodes)

def handle_dict(n1, n2):
		return mapreduce([a for (a, b) in n1.items], [a for (a, b) in n2.items]) \
			   and mapreduce([b for (a, b) in n1.items], [b for (a, b) in n2.items])

def handle_subscript(n1, n2):
		return dispatch(n1.expr, n2.expr) \
			   and dispatch(n1.subs[0], n2.subs[0])

def handle_if(n1, n2):
		return dispatch(n1.tests[0][0], n2.tests[0][0]) \
			   and dispatch(n1.tests[0][1], n2.tests[0][1]) \
			   and dispatch(n1.else_, n2.else_)

def handle_while(n1, n2):
		return dispatch(n1.test, n2.test) \
			   and dispatch(n1.body, n2.body)

def handle_ifexp(n1, n2):
        return dispatch(n1.test, n2.test) \
               and dispatch(n1.then, n2.then) \
               and dispatch(n1.else_, n2.else_)

def handle_stmt(n1, n2):
	return mapreduce(n1.nodes, n2.nodes)

def handle_module(n1, n2):
	return dispatch(n1.node, n2.node)

HANDLERS = \
{ \
		'Module'     : handle_module, \

		'Stmt'       : handle_stmt, \

		'Printnl'    : handle_printnl, \

		'Assign'     : handle_assign, \

		'AssName'    : handle_assname, \

		'Discard'    : handle_discard,  \

		'Const'      : handle_const, \

		'Name'       : handle_name, \

		'Add'        : handle_add, \

		'UnarySub'   : handle_unarysub, \

		'Function'   : handle_function, \

		'Lambda'     : handle_lambda, \

		'Return'     : handle_return, \

		'CallFunc'   : handle_callfunc, \

		'Compare'    : handle_compare, \

		'And'        : handle_and, \

		'Or'         : handle_or, \

		'Not'        : handle_not, \

		'List'       : handle_list, \

		'Dict'       : handle_dict, \

	    'Subscrtipt' : handle_subscript, \

		'If'         : handle_if, \

		'While'      : handle_while, \

		'IfExp'      : handle_ifexp \
}


def is_equal(n1, n2):
	return dispatch(n1, n2)

def main(argv):
	ast1 = compiler.parseFile(str(sys.argv[-1]))
	ast2 = compiler.parseFile(str(sys.argv[-2]))

	print is_equal(ast1, ast2)

if __name__ == "__main__":
     main(sys.argv[1:])
