from compiler.ast import *

def local_vars(n):
	if isinstance(n, Module):
        	return local_vars(n.node)
	elif isinstance(n, Stmt):
		print n
		fv_nodes = []
		#fv_nodes = [local_vars(e) for e in n.nodes]
		for e in n.nodes:
			if isinstance(e, Lambda) or isinstance(e, Function) or isinstance(e, Assign):
				fv_nodes.append(local_vars(e))
		if fv_nodes is not None:
			print fv_nodes
			local_in_nodes = reduce(lambda a, b: a | b, fv_nodes, set([]))
        	return local_in_nodes
    	elif isinstance(n, Printnl):
		e = local_vars(n.nodes[0])
		return e
    	elif isinstance(n, Assign):
		local_expr = set([])
		local_nodes = set([])
		#if isinstance(n.expr, list):
		#	fv_expr = []
		#	for e in n.nodes:
		#		if e is not None:
		#			fv_expr.append(local_vars(e))
		#	#fv_expr = [local_vars(e) for e in n.expr]
		#	local_expr = reduce(lambda a, b: a | b, fv_expr, set([]))
		#else:
		#	if n.expr is not None:
		#		local_expr = local_vars(n.expr)	
		for node in n.nodes:
			if isinstance(node, list):
				e = [local_vars(e) for e in node]
				local_nodes = local_nodes | reduce(lambda a, b: a | b, e, set([]))
			else:
				if node is not None:
					e = [local_vars(node)]
				local_nodes = reduce(lambda a, b: a | b, e, set([]))
		if local_nodes is not None:
		#	if local_expr is not None:
			return local_nodes
		#else:
		#	return local_nodes
		#return local_nodes | local_expr
    	elif isinstance(n, Discard):
		e = local_vars(n.expr)
		return e
	elif isinstance(n, Const):
		return set([])
	elif isinstance(n, Name):
		if n.name == 'True' or n.name == 'False':
			return set([])
		else:
			return set([n.name])
	elif isinstance(n, AssName):
		if n.name == 'True' or n.name == 'False':
			return set([])
		else:
			return set([n.name])
	elif isinstance(n, Add):
		#return local_vars(n.left) | local_vars(n.right)
		return set([])
	elif isinstance(n, UnarySub):
		return local_vars(n.expr)
	elif isinstance(n, CallFunc):
		fv_args = [local_vars(e) for e in n.args]
		local_in_args = reduce(lambda a, b: a | b, fv_args, set([]))
		return local_vars(n.node) | local_in_args
	elif isinstance(n, Lambda):
		if local_vars(n.code) is not None:
			if n.argnames is not None:
				return local_vars(n.code) - set(n.argnames)
			else:
				return local_vars(n.code)
		else:
			return set(n.argnames)
	elif isinstance(n, Function):
		if local_vars(n.code) is not None:
			if n.argnames is not None:
				return local_vars(n.code) - set(n.argnames)
			else:
				return local_vars(n.code)
		else:
			return set(n.argnames)
	elif isinstance(n, Return):
		return local_vars(n.value)
	elif isinstance(n, IfExp):
		test = local_vars(n.test)
		then = local_vars(n.then)
		else_= local_vars(n.else_)
		#return test | then | else_
		return set([])
    	elif isinstance(n, Compare):
		e = local_vars(n.expr)
		ops = local_vars(n.ops[0][1])
		return e | ops
    	elif isinstance(n, Subscript):
		e = local_vars(n.expr)
	        subs = local_vars(n.subs)
		return e | subs
    	elif isinstance(n, List):
		fv_expr = [local_vars(e) for e in n.nodes]
		local_in_expr = reduce(lambda a, b: a | b, fv_expr, set([]))
		return fv_expr | local_in_expr
    	elif isinstance(n, Dict):
		fv_items = [local_vars(e) for e in n.items]
		local_in_items = reduce(lambda a, b: a | b, fv_items, set([]))
		return fv_items | local_in_items
    	elif isinstance(n, And):
		return local_vars(n.nodes[0]) | local_vars(n.nodes[1])
    	elif isinstance(n, Or):
		return local_vars(n.nodes[0]) | local_vars(n.nodes[1])
    	elif isinstance(n, Not):
		return local_vars(n.expr)
	elif isinstance(n, GetTag):
		#return local_vars(n.arg)
		return set([])
        elif isinstance(n, InjectFrom):
		#return local_vars(n.arg)
		return set([])
        elif isinstance(n, ProjectTo):
		#return local_vars(n.arg)
		return set([])
        elif isinstance(n, Let):
		#rhs = local_vars(n.rhs)
		#body = local_vars(n.body)
		#return  body
		return set([])
	else:
		raise Exception('Error in local_vars: unrecognized AST node')

