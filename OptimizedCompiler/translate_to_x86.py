#!/usr/bin/python

import compiler
import sys, getopt, os
from x86_ast import *
from compiler.ast import *
from liveness_analysis import *
from generate_rig import *
from color_graph import *
from generate_spill_code import *
from explicate_ast import *
# meaningfully named constants
TEMP_COUNT = 0
ATOMIC     = 0
BINDINGS   = 1


# flatExprs: a list of flat expressions
# return: a map from variables to stack locations
def mapVarToAddr(flatExprs):
	varToAddrMap = {}
	varNum = 1
	for flatExpr in flatExprs:
		if isinstance(flatExpr, Assign) and flatExpr.nodes[0].name not in varToAddrMap.keys():
			varToAddrMap[flatExpr.nodes[0].name] = "-" + str(varNum*4) + "(%ebp)"
			varNum = varNum + 1
	return varToAddrMap



# flatExprs: flattened ast
# return: flattened x86 nodes
def translate_worker(flatExprs, func_dict):
	#varMap = mapVarToAddr(flatExprs)
	x86_stmts = []
	for flatExpr in flatExprs:
		if isinstance(flatExpr, Printnl):
			atomic = flatExpr.nodes[0]
			x86_stmts.append(Pushl(Name("%ecx")))
			x86_stmts.append(Pushl(Name("%edx")))
			x86_stmts.append(Pushl(Name("%eax")))
			x86_stmts.append(Pushl(atomic))
			x86_stmts.append(PrintX86(atomic))
			x86_stmts.append(Addl(Const(4), Name("%esp")))
			x86_stmts.append(Popl(Name("%eax")))
			x86_stmts.append(Popl(Name("%edx")))
			x86_stmts.append(Popl(Name("%ecx")))
		elif isinstance(flatExpr, Discard):
			x86_stmts.append(NOOP(flatExpr))
		elif isinstance(flatExpr, IfStmt):
			then = [] #[translate_worker([inst]) for inst in flatExpr.then]
			else_ = [] #[translate_worker([inst]) for inst in flatExpr.else_]
			for inst in flatExpr.then:
				then = then + translate_worker([inst], func_dict)
			for inst in flatExpr.else_:
				else_ = else_ + translate_worker([inst], func_dict)
			x86_stmts.append(IfStmt(then, flatExpr.test, else_))
		elif isinstance(flatExpr, While):
			test = []
			for inst in flatExpr.test[1]:
				test += translate_worker([inst], func_dict)
			flatExpr.test[1] = test
			body = []
			for inst in flatExpr.body:
				body += translate_worker([inst], func_dict)
			flatExpr.body = body
			x86_stmts.append(flatExpr)
		elif isinstance(flatExpr, Return):
			x86_stmts.append(Movl(flatExpr.value, Name("%eax")))
		elif isinstance(flatExpr, Assign):
			expr = flatExpr.expr
			if isinstance(expr, CallFunc):
				if expr.node.name == 'input' or expr.node.name == 'is_true':
					for a in expr.args:
						x86_stmts.append(Pushl(a))
					x86_stmts.append(Call(expr))
					x86_stmts.append(Movl(Name("%eax"), Name(flatExpr.nodes[0].name)))
					x86_stmts.append(Addl(Const(4*len(expr.args)), Name("%esp")))
				else:
					for a in expr.args:
						x86_stmts.append(Pushl(a))
					x86_stmts.append(Call(expr))
					x86_stmts.append(Movl(Name("%eax"), Name(flatExpr.nodes[0].name)))
					x86_stmts.append(Addl(Const(4*len(expr.args)), Name("%esp")))
			elif isinstance(expr, CreateClosure):
				print
				print "Closure expr"
				print expr
				print
				print "Closure flatExpr: Assign"
				print flatExpr
				print
				for a in expr.argnames:
					x86_stmts.append(Pushl(Name(a)))

				x86_stmts.append(Pushl(Name("$"+expr.name)))
				x86_stmts.append(Call(Name("create_closure")))
				x86_stmts.append(Movl(Name("%eax"), Name(flatExpr.nodes[0].name)))
				x86_stmts.append(Addl(Const(4), Name("%esp")))
				x86_stmts.append(Pushl(Name(flatExpr.nodes[0].name)))
				x86_stmts.append(Call(Name('inject_big')))
				x86_stmts.append(Movl(Name("%eax"), Name(flatExpr.nodes[0].name)))
				x86_stmts.append(Addl(Const(4), Name("%esp")))

			elif isinstance(expr, IndirectCallFunc):
				for a in expr.args:
					if not isinstance(a, Name):
						a = Name(a)
					x86_stmts.append(Pushl(a))
				x86_stmts.append(Pushl(expr.free_vars))
				x86_stmts.append(Call(Name(expr.func_ptr.name)))
				x86_stmts.append(Movl(Name("%eax"), Name(flatExpr.nodes[0].name)))
				x86_stmts.append(Addl(Const(4+(4*len(expr.args))), Name("%esp")))
			elif isinstance(expr, Add):
				if (isinstance(flatExpr.nodes[0], Name) and expr.right.name == flatExpr.nodes[0].name):
					x86_stmts.append(Addl(expr.left, Name(flatExpr.nodes[0].name)))
				else:
					x86_stmts.append(Movl(expr.left, Name(flatExpr.nodes[0].name)))
					x86_stmts.append(Addl(expr.right, Name(flatExpr.nodes[0].name)))
			elif isinstance(expr, UnarySub):
				if isinstance(expr.expr, Const):
					x86_stmts.append(Movl(expr.expr, Name(flatExpr.nodes[0].name)))
					x86_stmts.append(Negl(Name(flatExpr.nodes[0].name)))
				else:
					x86_stmts.append(Movl(Name(expr.expr.name), Name(flatExpr.nodes[0].name)))
					x86_stmts.append(Negl(Name(flatExpr.nodes[0].name)))
			elif isinstance(expr, GetTag):
				x86_stmts.append(Pushl(expr.arg))
				if expr.typ == "BIGPYOBJ":
					x86_stmts.append(Pushl(expr.arg))
					x86_stmts.append(Call(Name('is_big')))
					x86_stmts.append(Movl(Name('%eax'), Name(flatExpr.nodes[0].name)))
				else:
					x86_stmts.append(Call(Name('is_' + expr.typ.lower())))
				x86_stmts.append(Movl(Name('%eax'), Name(flatExpr.nodes[0].name)))
				x86_stmts.append(Addl(Const(4), Name("%esp")))
			elif isinstance(expr, InjectFrom):
				if expr.typ == "INT":
					x86_stmts.append(Pushl(expr.arg))
					x86_stmts.append(Call(Name('inject_int')))
					x86_stmts.append(Movl(Name('%eax'), Name(flatExpr.nodes[0].name)))
				elif expr.typ == "BOOL":
					x86_stmts.append(Pushl(expr.arg))
					x86_stmts.append(Call(Name('inject_bool')))
					x86_stmts.append(Movl(Name('%eax'), Name(flatExpr.nodes[0].name)))
				elif expr.typ == "BIGPYOBJ":
					x86_stmts.append(Pushl(expr.arg))
					x86_stmts.append(Call(Name('inject_big')))
					x86_stmts.append(Movl(Name('%eax'), Name(flatExpr.nodes[0].name)))
				x86_stmts.append(Addl(Const(4), Name("%esp")))
			elif isinstance(expr, ProjectTo):
				if expr.typ == "INT":
					x86_stmts.append(Pushl(expr.arg))
					x86_stmts.append(Call(Name('project_int')))
					x86_stmts.append(Movl(Name('%eax'), Name(flatExpr.nodes[0].name)))
				elif expr.typ == "BOOL":
					x86_stmts.append(Pushl(expr.arg))
					x86_stmts.append(Call(Name('project_bool')))
					x86_stmts.append(Movl(Name('%eax'), Name(flatExpr.nodes[0].name)))
				elif expr.typ == "BIGPYOBJ":
					x86_stmts.append(Pushl(expr.arg))
					x86_stmts.append(Call(Name('project_big')))
					x86_stmts.append(Movl(Name('%eax'), Name(flatExpr.nodes[0].name)))
				x86_stmts.append(Addl(Const(4), Name("%esp")))
			elif isinstance(expr, List):
					x86_stmts.append(Pushl(Const(len(expr.nodes))))
					x86_stmts.append(Call(Name('inject_int')))
					x86_stmts.append(Pushl(Name('%eax')))
					x86_stmts.append(Call(Name('create_list')))
					x86_stmts.append(Pushl(Name('%eax')))
					x86_stmts.append(Call(Name('inject_big')))
					x86_stmts.append(Movl(Name('%eax'), Name(flatExpr.nodes[0].name)))
					if len(expr.nodes):
						for i in range(len(expr.nodes)):
							x86_stmts.append(Pushl(Const(i)))
							x86_stmts.append(Call(Name('inject_int')))
							x86_stmts.append(Pushl(expr.nodes[i]))
							x86_stmts.append(Pushl(Name('%eax')))
							x86_stmts.append(Pushl(Name(flatExpr.nodes[0].name)))
							x86_stmts.append(Call(Name('set_subscript')))
					x86_stmts.append(Addl(Const(12+(4*len(expr.nodes))), Name("%esp")))
			elif isinstance(expr, Subscript):
				if expr.flags == "OP_APPLY":
					#x86_stmts.append(Pushl(Const(1)))
					#x86_stmts.append(Call(Name('inject_int')))
					x86_stmts.append(Pushl(expr.subs))
					#x86_stmts.append(Pushl(Name("%eax")))
					x86_stmts.append(Pushl(expr.expr))
					x86_stmts.append(Call(Name('get_subscript')))
					x86_stmts.append(Movl(Name("%eax"), Name(flatExpr.nodes[0].name)))
					x86_stmts.append(Addl(Const(8), Name("%esp")))
				else:
					x86_stmts.append(Pushl(expr.subs))
					x86_stmts.append(Call(Name('inject_int')))
					#x86_stmts.append(Pushl(flatExpr.expr))
					#x86_stmts.append(Pushl(expr.subs))
					x86_stmts.append(Pushl(Name("%eax")))
					x86_stmts.append(Pushl(expr.expr))
					x86_stmts.append(Call(Name('set_subscript')))
					x86_stmts.append(Addl(Const(12), Name("%esp")))
					#x86_stmts.append(Movl(Name("%eax"), Name(flatExpr.nodes[0].name)))
					#x86_stmts.append(Addl(Const(4*len(expr.args)), Name("%esp")))
			elif isinstance(expr, Dict):
					x86_stmts.append(Pushl(Const(len(expr.items))))
					x86_stmts.append(Call(Name('inject_int')))
					x86_stmts.append(Pushl(Name('%eax')))
					x86_stmts.append(Call(Name('create_dict')))
					x86_stmts.append(Pushl(Name('%eax')))
					x86_stmts.append(Call(Name('inject_big')))
					x86_stmts.append(Movl(Name('%eax'), Name(flatExpr.nodes[0].name)))
					for item in expr.items:
						x86_stmts.append(Pushl(item[1]))
						x86_stmts.append(Pushl(item[0]))
						x86_stmts.append(Pushl(Name(flatExpr.nodes[0].name)))
						x86_stmts.append(Call(Name('set_subscript')))
			elif isinstance(expr, Compare):
			#	if expr.ops[0][0] == "is":
			#		print "is"
				#"""
			#	x86_stmts.append(Pushl(expr.expr))
			#	x86_stmts.append(Call(Name('project_int')))
			#	x86_stmts.append(Movl(Name('%eax')),)
			#	x86_stmts.append(Pushl(expr.ops[0][1]))
			#	x86_stmts.append(Call(Name('project_int')))
			#	x86_stmts.append(Pushl(Name('%eax')))
			#	x86_stmts.append(Cmpl(expr.expr, expr.ops))
				#x86_stmts.append(Movl(expr.expr, Name(flatExpr.nodes[0].name)))
				x86_stmts.append(x86Compare(expr.expr, expr.ops, Name(flatExpr.nodes[0].name)))
			#	"""
				#if expr.ops[0][0] == "==":
					#x86_stmts.append(Cmpl(expr.expr, expr.ops[0][1]))
			#		x86_stmts.append(Movl(expr.expr, expr.ops[0][1]))
			elif isinstance(expr, AssName):
				x86_stmts.append(Movl(Name(expr.name), Name(flatExpr.nodes[0].name)))
			elif isinstance(expr, Const):
					x86_stmts.append(Movl(expr, Name(flatExpr.nodes[0].name)))
			elif isinstance(expr, Name):
				if isinstance(flatExpr.nodes[0], AssName):
						x86_stmts.append(Movl(Name(expr.name), Name(flatExpr.nodes[0].name)))
				else: # expr.flags == "OP_APPLY":
					x86_stmts.append(Pushl(flatExpr.nodes[0].subs[0]))
					x86_stmts.append(Call(Name('inject_int')))
					#x86_stmts.append(Pushl(expr.subs))
					x86_stmts.append(Pushl(flatExpr.expr))
					#x86_stmts.append(Movl(Name('%eax'), flatExpr.nodes[0].expr))
					#x86_stmts.append(Pushl(flatExpr.nodes[0].subs[0]))
					x86_stmts.append(Pushl(Name("%eax")))
					x86_stmts.append(Pushl(flatExpr.nodes[0].expr))
					x86_stmts.append(Call(Name('set_subscript')))
					#x86_stmts.append(Pushl(Name('%eax')))
					#x86_stmts.append(Call(Name('inject_big')))

					#x86_stmts.append(Pushl(Name('%eax')))
					#x86_stmts.append(Call(Name('print_any')))
			#		else:
			#			x86_stmts.append(Movl(Name(expr.name), Name(flatExpr.nodes.name)))
			elif isinstance(expr, Lambda):
				code = []
				if isinstance(expr.code, list):
					for element in expr.code:
						code += translate_worker([element], func_dict)
						#print code
				else:
					code = translate_worker(expr.code, func_dict)
				func_dict[flatExpr.nodes[0].name] = code
			else:
				print
				print expr
				raise Exception('error in translate_worker: invalid assign 1')
		elif isinstance(flatExpr, Lambda):
			code = []
			if isinstance(flatExpr.code, list):
				for element in flatExpr.code:
					code += translate_worker([element], func_dict)
					#print code
			else:
				code = translate_worker(flatExpr.code, func_dict)
			func_dict[flatExpr.defaults] = [code, flatExpr.argnames]
		else:
			print
			print flatExpr
			raise Exception('error in translate_worker: invalid assign 2')
	return x86_stmts #[x86_stmts, len(varMap.keys())]


def translate_to_x86(n):
	func_dict = {}
	func_dict['main'] = [translate_worker(n, func_dict), []]
	return func_dict


