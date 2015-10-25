from compiler import *
from explicate_ast import *

TEMP_COUNT = 0
LAMBDA_COUNT = 0
ATOMIC = 0
# return: the next variable name
def get_variable_name_explicate():
    global TEMP_COUNT
    variable_name = "exp_temp$" + str(TEMP_COUNT)
    TEMP_COUNT = TEMP_COUNT + 1
    return variable_name

def get_lambda_name():
    global LAMBDA_COUNT
    variable_name = "lambda$_" + str(LAMBDA_COUNT)
    LAMBDA_COUNT = LAMBDA_COUNT + 1
    return variable_name

def is_true(n):
	call_func = CallFunc(Name('is_true'), [n], None, None)
	return InjectFrom('BOOL', call_func)

def generate_ifexp(test, then, else_):
    return IfExp(test, then,  else_)

def generate_mix_compare(var1, var2, e1, e2, op, typ):
		if typ == 1:
			return InjectFrom('BOOL', Compare(ProjectTo('INT',  var1), [(op, ProjectTo('BOOL', var2))]))
		elif typ == 2:
			return InjectFrom('BOOL', Compare(ProjectTo('BOOL',  var1), [(op, ProjectTo('INT', var2))]))
		else:
			if op == "!=":
				return InjectFrom('BOOL', Const(1))
			else:
				return InjectFrom('BOOL', Const(0))

def generate_big_case(var1, var2, e1, e2, op):
	func_name = ''
	if op == "==":
		func_name = Name('equal')
	else:
		func_name = Name('not_equal')
	return InjectFrom('BOOL', CallFunc(func_name, [ProjectTo('BIGPYOBJ',  var1), ProjectTo('BIGPYOBJ', var2)], None, None))

def explicate_ast(n):
    if isinstance(n, Module):
        return explicate_ast(n.node)
    elif isinstance(n, Stmt):
        explicated_stmt = []
        for node in n.nodes:
            e = explicate_ast(node)
            if isinstance(e, list):
                explicated_stmt = explicated_stmt + e
            else:
                explicated_stmt.append(e)
        return Stmt(explicated_stmt)
    elif isinstance(n, Printnl):
        explicated = explicate_ast(n.nodes[0])
        var = Name(get_variable_name_explicate())
        var1 = get_variable_name_explicate()
        n = Let(var, explicated, CallFunc(Name('print_any'), [var], None, None))
        return n
    elif isinstance(n, Assign):
        nodes = explicate_ast(n.nodes[0])
        expr = explicate_ast(n.expr)
        return Assign(n.nodes, expr)
    elif isinstance(n, AssName):
        return n #AssName(Name(n.name), n.flags)
    elif isinstance(n, Discard):
        explicate_result = explicate_ast(n.expr)
        return Discard(explicate_result)
    elif isinstance(n, Const):
        n = InjectFrom('INT', Const(n.value))
        return n
    elif isinstance(n, Name):
        if(n.name == 'True'):
            n = InjectFrom('BOOL', Const(1))
        elif(n.name == 'False'):
            n = InjectFrom('BOOL', Const(0))
        return n
    elif isinstance(n, Add):
        res_l = explicate_ast(n.left)
        res_r = explicate_ast(n.right)
        temp_l = Name(get_variable_name_explicate())
        temp_r = Name(get_variable_name_explicate())

        callf1 = InjectFrom('BIGPYOBJ', CallFunc(Name('add'),[ProjectTo('BIGPYOBJ',temp_r), ProjectTo('BIGPYOBJ',temp_l)],None, None))

        return Let(temp_l, res_l, Let(temp_r, res_r, \
                  IfExp(GetTag('INT', temp_l), InjectFrom('INT', Add((ProjectTo('INT', temp_l), ProjectTo('INT', temp_r)))), \
                  IfExp(GetTag('BOOL', temp_l), InjectFrom('INT', Add((ProjectTo('BOOL', temp_l), ProjectTo('BOOL', temp_r)))), \
                  callf1))))
    elif isinstance(n, UnarySub):
        if isinstance(n.expr, Const):
            return InjectFrom('INT', Const(-n.expr.value))
        elif isinstance(n.expr, Name):
            if (n.expr.name == "True"):
                return InjectFrom('INT', Const(-1))
            elif (n.expr.name == "False"):
                return InjectFrom('INT', Const(0))

        res = explicate_ast(n.expr)
        return InjectFrom('INT', UnarySub(ProjectTo('INT', res)))
        res = explicate_ast(n.expr)
    elif isinstance(n, Function):
	#argnames = n.argnames if n.argnames[0] is not None else []
	return Assign([AssName(n.name, 'OP_ASSIGN')], Lambda(n.argnames, [], n.flags, explicate_ast(n.code)))
    elif isinstance(n, Lambda):
	argnames = n.argnames if len(n.argnames) == 0 or n.argnames[0] is not None else []
	return Lambda(argnames, n.defaults, n.flags, Stmt([Return(explicate_ast(n.code))]))
    elif isinstance(n, Return):
	value = explicate_ast(n.value)
	return Return(value)
    elif isinstance(n, GetTag):
        arg = explicate_ast(n.arg)
        return GetTag(n.typ, arg)
    elif isinstance(n, CallFunc):
        node = explicate_ast(n.node)
        args = []
        if isinstance(n.args, list):
	    args = [explicate_ast(arg) for arg in n.args]
   	else:
            args = explicate_ast(n.args)
        if isinstance(n.node, Name) and n.node.name == 'input':
            var = Name(get_variable_name_explicate())
            return Let(var, CallFunc(node, args), InjectFrom('INT', var))
        else:
            return IndirectCallFunc(node, '', args)
    elif isinstance(n, Compare):  #new
        e1 = explicate_ast(n.expr)
        op = n.ops[0][0]
        e2 = explicate_ast(n.ops[0][1])

        if op == "is":
            return InjectFrom('BOOL', Compare(e1, [(op, e2)]))

        e1_var = Name(get_variable_name_explicate())
        e2_var = Name(get_variable_name_explicate())

        int_case = InjectFrom('BOOL', Compare(ProjectTo('INT',  e1_var), [(op, ProjectTo('INT', e2_var))]))
        bool_case = InjectFrom('BOOL', Compare(ProjectTo('BOOL',  e1), [(op, ProjectTo('BOOL', e2))]))
        mix_case1 = generate_mix_compare(e1_var, e2_var, e1, e2, op, 1)
        mix_case2 = generate_mix_compare(e1_var, e2_var, e1, e2, op, 2)
        mix_case3 = generate_mix_compare(e1_var, e2_var, e1, e2, op, 3)
        big_case = generate_big_case(e1_var, e2_var, e1, e2, op)

        return Let(e1_var, e1, Let(e2_var, e2, \
               IfExp(GetTag('INT', e1_var), \
                IfExp(GetTag('INT', e2_var), \
                 int_case, \
                 IfExp(GetTag('BOOL', e2_var), \
                  mix_case1, \
                  InjectFrom('BOOL', Const(0)))), \
               	IfExp(GetTag('BOOL', e1_var), \
                 IfExp(GetTag('BOOL', e2_var), \
                  bool_case, \
                  IfExp(GetTag('INT', e2_var), \
                   mix_case2, \
                   InjectFrom('BOOL', Const(0)))), \
                 #IfExp(GetTag('BIGPYOBJ', e1_var), \
                 IfExp(GetTag('BIGPYOBJ', e1_var), \
                   big_case, \
                   mix_case3)))))
    elif isinstance(n, And):      #new
        n0 = explicate_ast(n.nodes[0])
        n1 = explicate_ast(n.nodes[1])
        n0_is_true =  is_true(n0)
        var = Name(get_variable_name_explicate())
        return Let(var, n0_is_true, IfExp(ProjectTo('BOOL', var), n1, n0))
    elif isinstance(n, Or):       #new
        n0 = explicate_ast(n.nodes[0])
        n1 = explicate_ast(n.nodes[1])
        n0_is_true =  is_true(n0)
        var = Name(get_variable_name_explicate())
        return Let(var, n0_is_true, IfExp(ProjectTo('BOOL', var), n0, n1))
    elif isinstance(n, Not):      #new
        e = explicate_ast(n.expr)
        e_is_true = is_true(e)
        var = Name(get_variable_name_explicate())
	#print n.expr
	if isinstance(n.expr, Name) and (n.expr.name == 'True' or n.expr.name == 'False'):
		stmt = IfExp(ProjectTo('BOOL', var), InjectFrom('BOOL', Name('False')), InjectFrom('BOOL', Name('True')))
	else:
        	stmt = IfExp(ProjectTo('BOOL', var), InjectFrom('BOOL', Const(0)), InjectFrom('BOOL', Const(1)))
        return Let(var, e_is_true, stmt) #IfExp(var, InjectFrom('BOOL', Name('True')), InjectFrom('BOOL', Name('False'))))
    elif isinstance(n, List):     #new
        e = []
        for n in n.nodes:
            e.append(explicate_ast(n))
        #return InjectFrom('BIGPYOBJ', List(e))
        return List(e)
    elif isinstance(n, Dict):     #new
        exp_items = []
        for n in n.items:
            key = explicate_ast(n[0])
            val = explicate_ast(n[1])
            exp_items.append((key, val))
        return Dict(exp_items)
    elif isinstance(n, Subscript):     #new
        explicated_expr =  explicate_ast(n.expr)
        explicated_sub  = explicate_ast(n.subs[0])
        return Subscript(explicated_expr, n.flags, explicated_sub)
    elif isinstance(n, If):
		test = explicate_ast(n.tests[0][0])
		then = explicate_ast(n.tests[0][1])
		else_ = explicate_ast(n.else_)
		is_test = is_true(test)
		tests = (ProjectTo("BOOL", is_test), then)
		return If([tests], else_)
    elif isinstance(n, While):
	test = explicate_ast(n.test)
	n.test = (ProjectTo("BOOL", is_true(test)))
	n.body = explicate_ast(n.body)
	return n
    elif isinstance(n, IfExp):
	is_primitive = False
        test = explicate_ast(n.test)
        then = explicate_ast(n.then)
        else_= explicate_ast(n.else_)

	if isinstance(test, InjectFrom):
		if isinstance(test.arg, Const):
			is_primitive = True
	elif isinstance(test, List):
		if not test.nodes:
			test = InjectFrom('INT', Const(0))
	elif isinstance(test, Dict):
		if not test.items:
			test = InjectFrom('INT', Const(0))
        is_test = is_true(test)
        call_error = CallFunc(Name('error_pyobj'), None, None, None)

        test_var = Name(get_variable_name_explicate())
        then_var = Name(get_variable_name_explicate())
        else_var = Name(get_variable_name_explicate())

        # Create code for out cases
        #int_case = explicate_ast(And([GetTag('INT', then), GetTag('INT',else_)]))
        #bool_case = explicate_ast(And([GetTag('BOOL', then), GetTag('BOOL',else_)]))
        #big_case = explicate_ast(And([GetTag('BIGPYOBJ', then), GetTag('BIGPYOBJ',else_)]))
	if is_primitive:
        	stmt = IfExp(ProjectTo('BOOL', is_test), then, else_)
	else:
        	stmt = IfExp(ProjectTo('BOOL', test_var), then, else_)
        int_stmt = InjectFrom('INT', IfExp(test_var, then_var, else_var))
        bool_stmt = InjectFrom('BOOL', IfExp(ProjectTo('BOOL', test_var), ProjectTo('BOOL', then), ProjectTo('BOOL', else_)))
        big_stmt = InjectFrom('BIGPYOBJ', IfExp(ProjectTo('BOOL', test_var), ProjectTo('BIGPYOBJ', then), ProjectTo('BIGPYOBJ', else_)))

        """return Let(test_var, test, Let(then_var, then, Let(else_var, else_, \
               IfExp(GetTag('INT', then_var), \
                 int_stmt, \
               IfExp(GetTag('BOOL', then_var), \
                IfExp(GetTag('BOOL', else_var), \
                 bool_stmt, \
                 call_error), \
                IfExp(GetTag('BIGPYOBJ', else_var), \
                 big_stmt, \
                 call_error))))))
        """
        #return IfExp(GetTag('BOOL', is_test), IfExp(int_case, int_stmt, IfExp(bool_case, bool_stmt, IfExp(big_case, big_stmt, CallFunc(Name('error_pyobj'), None, None, None)))), CallFunc(Name('error_pyobj'), None, None, None))
        #return Let(test_var, is_test, IfExp(GetTag('BOOL', test_var), stmt, CallFunc(Name('error_pyobj'), None, None, None)))
        return Let(test_var, is_test, stmt)
        #then_var = Name(get_variable_name_explicate())
        #else_var = Name(get_variable_name_explicate())

        """return IfExp(GetTag('BOOL', is_test), \
                 Let(then_var, then, Let(else_var, else_, \
                   IfExp(GetTag('INT', then_var), \
                   IfExp(GetTag('INT', else_var), \
                     IfExp(is_test, ProjectTo('INT', then_var), ProjectTo('INT', else_var)), call_error), \
                   IfExp(GetTag('BOOL', then_var), \
                   IfExp(GetTag('BOOL', else_var), \
                     IfExp(is_test, ProjectTo('BOOL', then_var), ProjectTo('BOOL', else_var)), call_error), \
                   IfExp(GetTag('BIGPYOBJ', then_var), \
                   IfExp(GetTag('BIGPYOBJ', else_var), \
                     IfExp(is_test, ProjectTo('BIGPYOBJ', then_var), ProjectTo('BIGPYOBJ', else_var)), call_error), \
                     call_error))))), \
                   call_error)
        """
    else:
        print "Error"
        print n
        raise Exception('Error in explicate_ast: unrecognized AST node')

