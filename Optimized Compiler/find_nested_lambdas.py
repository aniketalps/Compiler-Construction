from compiler import *
from freevars import *

free_vars_set = set([])

def find_nested_lambdas(n):
	global free_vars_set
	if isinstance(n, Module):
        	return find_nested_lambdas(n.node)
	elif isinstance(n, Stmt):
		fv_nodes = []
		#fv_nodes = [find_nested_lambdas(e) for e in n.nodes]
		for e in n.nodes:
			if isinstance(e, Lambda) or isinstance(e, Function) or isinstance(e, Assign):
				print e
				fv_nodes.append(find_nested_lambdas(e))
		if fv_nodes is not None:
			lambda_in_nodes = reduce(lambda a, b: a | b, fv_nodes, set([]))
        	return lambda_in_nodes
    	elif isinstance(n, Printnl):
		e = find_nested_lambdas(n.nodes[0])
		return e
    	elif isinstance(n, Assign):
		lambda_expr = set([])
		lambda_nodes = set([])
		if isinstance(n.expr, list):
			for e in n.expr:
				if e is not None:	
					lambda_expr.append(find_nested_lambdas(e))
		else:
			if n.expr is not None:
				#print n.expr
				lambda_expr = [find_nested_lambdas(n.expr)]
		lambda_expr = reduce(lambda a, b: a | b, lambda_expr, set([]))
			
		for node in n.nodes:
			if isinstance(node, list):
				e = [find_nested_lambdas(e) for e in node]
				print e
				lambda_nodes = lambda_nodes | reduce(lambda a, b: a | b, e, set([]))
			else:
				if node is not None:
					e = [find_nested_lambdas(node)]
					print e
					lambda_nodes = reduce(lambda a, b: a | b, e, set([]))
		return lambda_nodes | lambda_expr
    	elif isinstance(n, Discard):
		e = find_nested_lambdas(n.expr)
		return e
	elif isinstance(n, Const):
		return set([])
	elif isinstance(n, Name):
			return set([])
	elif isinstance(n, AssName):
		return set([])
	elif isinstance(n, Add):
		return find_nested_lambdas(n.left) | find_nested_lambdas(n.right)
	elif isinstance(n, UnarySub):
		return find_nested_lambdas(n.expr)
	elif isinstance(n, CallFunc):
		fv_args = [find_nested_lambdas(e) for e in n.args]
		lambda_in_args = reduce(lambda a, b: a | b, fv_args, set([]))
		return find_nested_lambdas(n.node) | lambda_in_args
	elif isinstance(n, Lambda):
		if free_vars(n.code) is not None:
			if n.argnames is not None:
				free = free_vars(n.code) - set(n.argnames)
				free_vars_set = free_vars_set | free
				
			else:
				free_vars_set = free_vars_set | free_vars(n.code)
		else:
			free_vars_set = free_vars_set | set(n.argnames)

		find_nested_lambdas(n.code)
		return free_vars_set
	elif isinstance(n, Function):
		if free_vars(n.code) is not None:
			if n.argnames is not None:
				free = free_vars(n.code) - set(n.argnames)
				free_vars_set = free_vars_set | free
				
			else:
				free_vars_set = free_vars_set | free_vars(n.code)
		else:
			free_vars_set = free_vars_set | set(n.argnames)

		find_nested_lambdas(n.code)
		return free_vars_set
	elif isinstance(n, Return):
		return find_nested_lambdas(n.value)
	elif isinstance(n, IfExp):
		test = find_nested_lambdas(n.test)
		then = find_nested_lambdas(n.then)
		else_= find_nested_lambdas(n.else_)
		return test | then | else_
    	elif isinstance(n, Compare):
		e = find_nested_lambdas(n.expr)
		ops = find_nested_lambdas(n.ops[0][1])
		return e | ops
    	elif isinstance(n, Subscript):
		e = find_nested_lambdas(n.expr)
	        subs = find_nested_lambdas(n.subs)
		return e | subs
    	elif isinstance(n, List):
		fv_expr = [find_nested_lambdas(e) for e in n.nodes]
		lambda_in_expr = reduce(lambda a, b: a | b, fv_expr, set([]))
		return fv_expr | lambda_in_expr
    	elif isinstance(n, Dict):
		fv_items = [find_nested_lambdas(e) for e in n.items]
		lambda_in_items = reduce(lambda a, b: a | b, fv_items, set([]))
		return fv_items | lambda_in_items
    	elif isinstance(n, And):
		return find_nested_lambdas(n.nodes[0]) | find_nested_lambdas(n.nodes[1])
    	elif isinstance(n, Or):
		return find_nested_lambdas(n.nodes[0]) | find_nested_lambdas(n.nodes[1])
    	elif isinstance(n, Not):
		return find_nested_lambdas(n.expr)
	elif isinstance(n, GetTag):
		return set([])
		#return find_nested_lambdas(n.arg)
        elif isinstance(n, InjectFrom):
		#return find_nested_lambdas(n.arg)
		return set([])
        elif isinstance(n, ProjectTo):
		#return find_nested_lambdas(n.arg)
		return set([])
        elif isinstance(n, Let):
		rhs = find_nested_lambdas(n.rhs)
		body = find_nested_lambdas(n.body)
		return rhs | body
	else:
		raise Exception('Error in find_nested_lambdas: unrecognized AST node')

