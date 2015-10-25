#!/usr/bin/python

import compiler
import sys, getopt, os
from x86_ast import *
from compiler.ast import *
from liveness_analysis import *
from generate_rig import *
from color_graph import *
from generate_spill_code import *

# meaningfully named constants
TEMP_COUNT = 0
ATOMIC     = 0
BINDINGS   = 1

# Write the prologue of the .s file
# numVars: the number of variabl`es used by the program
# return: a list of instructions corresponding to the prologue
def getPrologue(func_name, numVars, func_args, mapping):
	space = "		"
	if func_name != "main":
		prologueStatement = ['\n' +".global " + func_name, func_name + ":", space + "pushl %ebp", space + "movl %esp, %ebp", space + "pushl %ebx", space + "pushl %esi", space + "pushl %edi"]
	else:
		prologueStatement = [".global " + func_name, func_name + ":", space + "pushl %ebp", space + "movl %esp, %ebp"]

	# Set up the function arguments
	i = 0
	for arg in func_args:
		argnum = '%s' % (8 + (4*i))
		i += 1
		if isinstance(arg, Name):
			if arg.name in mapping.keys():
				if ('-' in mapping[arg.name]):
					prologueStatement.append(space + "pushl %ebx")
					prologueStatement.append(space + "movl " + argnum + "(%ebp), %ebx")
					prologueStatement.append(space + "movl %ebx, " + mapping[arg.name])
					prologueStatement.append(space + "popl %ebx")
				else:
					prologueStatement.append(space + "movl " + argnum + "(%ebp), " + mapping[arg.name])
		else:
			if arg in mapping.keys():
				if ('-' in mapping[arg]):
					prologueStatement.append(space + "pushl %ebx")
					prologueStatement.append(space + "movl " + argnum + "(%ebp), %ebx")
					prologueStatement.append(space + "movl %ebx, " + mapping[arg])
					prologueStatement.append(space + "popl %ebx")
				else:
					prologueStatement.append(space + "movl " + argnum + "(%ebp), " + mapping[arg])
	if (numVars > 0):
		prologueStatement.append(space + "subl " + "$" + str(numVars*4) + ", %esp")
	return prologueStatement

# Write the epilogue of the program
# return: the a list of assembly instructions corresponding to the epilogue
def getEpilogue(func_name):
	space = "		"
	if func_name == "main":
		return [space + "movl $0, %eax", space + "leave", space + "ret"]
	return [space + "popl %edi",space + "popl %esi", space + "popl %ebx", space + "leave", space + "ret"]

# Write the body of the program
# x86Stmts: a list of x86 AST nodes
#return: a list of assembly instructions corresponding to the body
def getBody(x86Stmts, mapping):
	space = "		"
	code = []
	for stmt in x86Stmts:
		if isinstance(stmt, Pushl):
			if isinstance(stmt.node, Const):
				code.append(space + "pushl " + "$" + str(stmt.node.value))
			elif isinstance(stmt.node, Name):
				if "func$" in stmt.node.name:
					code.append(space + "pushl " + stmt.node.name)
				else:
					code.append(space + "pushl " + mapping[stmt.node.name])
			else:
				if stmt.node:
					code.append(space + "pushl " + mapping[stmt.node])
		elif isinstance(stmt, Popl):
			code.append(space + "popl " + mapping[stmt.node.name])
		elif isinstance(stmt, Movl):
			if isinstance(stmt.left, Const):
				code.append(space + "movl " + "$" + str(stmt.left.value) + ", " + mapping[stmt.right.name])
			else:
				if (('-' in mapping[stmt.left.name]) and ('-' in mapping[stmt.right.name])):
					code.append(space + "pushl %ebx")
					code.append(space + "movl " + mapping[stmt.left.name] + ", %ebx")
					code.append(space + "movl %ebx, " + mapping[stmt.right.name])
					code.append(space + "popl %ebx")
				else:
					code.append(space + "movl " + mapping[stmt.left.name] + ", " + mapping[stmt.right.name])
		elif isinstance(stmt, Addl):
			if isinstance(stmt.left, Const):
				code.append(space + "addl " + "$" + str(stmt.left.value) + ", " + mapping[stmt.right.name])
			else:
				if (('-' in mapping[stmt.left.name]) and ('-' in mapping[stmt.right.name])):
					code.append(space + "pushl %ebx")
					code.append(space + "movl " + mapping[stmt.left.name] + ", %ebx")
					code.append(space + "addl %ebx, " +  mapping[stmt.right.name])
					code.append(space + "popl %ebx")
				else:
					code.append(space + "addl " + mapping[stmt.left.name] + ", " + mapping[stmt.right.name])
		elif isinstance(stmt, Call):
			if isinstance(stmt.node, Name):
				if "$" in stmt.node.name and "func" not in stmt.node.name:
					code.append(space + "call *" + mapping[stmt.node.name])
				else:
					code.append(space + "call " + stmt.node.name)
			if isinstance(stmt.node, CallFunc):
				code.append(space + "call " + stmt.node.node.name)
		elif isinstance(stmt, PrintX86):
			code.append(space + "call print_int_nl")
		elif isinstance(stmt, Negl):
			code.append(space + "negl " + mapping[stmt.node.name])
		#elif isinstance(stmt, Cmpl):
		#	code.append(space + "cmpl " + mapping[stmt.expr.name]+ ", " + mapping[stmt.op2.name])
		elif isinstance(stmt, Andl):
			code.append(space + "andl " + mapping[stmt.op1.name]+ ", " + mapping[stmt.op2.name])
		elif isinstance(stmt, Orl):
			code.append(space + "orl " + mapping[stmt.op1.name]+ ", " + mapping[stmt.op2.name])
		elif isinstance(stmt, Notl):
			code.append(space + "notl " + mapping[stmt.expr.name])
		elif isinstance(stmt, NOOP):
			code.append(space + "NOP")
		elif isinstance(stmt, Cmpl):
			if isinstance(stmt.op1, Const):
				code.append(space + "cmpl " + "$" + str(stmt.op1.value) + ", " + mapping[stmt.op2.name])
			else:
				code.append(space + "cmpl " + mapping[stmt.op1.name] + ", " + mapping[stmt.op2.name])
		elif isinstance(stmt, JmpEqual):
			code.append(space + "je " + stmt.label)
		elif isinstance(stmt, JmpTo):
			code.append(space + "jmp " + stmt.label)
		elif isinstance(stmt, Label):
			code.append(stmt.label)
		else:
			print
			print
			print stmt
			raise Exception('Error in prettyPrint: no class')
	return code

# x86Stmts: a list of flattened x86 nodes
# numVars: the total number of vaiables in the list of instructions
# return: a list 'pretty' assembly code
def prettyPrint(func, x86Stmts, numVars, mapping, func_args):
	print
	print "FUNC ARGS"
	print func
	print func_args
	print
	prologue = getPrologue(func, numVars, func_args, mapping)
	codeBody = getBody(x86Stmts, mapping)
	epilogue = getEpilogue(func)
	return prologue + codeBody + epilogue
