import compiler
import sys, getopt, os
from x86_ast import *
from compiler.ast import *
from explicate_ast import *

TEMP_COUNT = 0

# return: the next variable name
def get_spill_var_name():
    global TEMP_COUNT
    variable_name = "unspillable$" + str(TEMP_COUNT)
    TEMP_COUNT = TEMP_COUNT + 1
    return variable_name


def generate_spill_code(instructions, spilled, spill_num):
	"""Iterate over the instructions.
	   look for two memory access and assign
       an unspillable variable name to the second
	   argument"""
	generated_code = []
	spill_count = 0
	global TEMP_COUNT
	TEMP_COUNT = spill_num
	for instruction in instructions:
		if isinstance(instruction, Movl)           \
		   and isinstance(instruction.left, Name)  \
		   and (instruction.right.name in spilled.keys()) \
		   and (instruction.left.name in spilled.keys()):
				spill_var = get_spill_var_name()
				generated_code.append(Movl(instruction.left, Name(spill_var)))
				generated_code.append(Movl(Name(spill_var), instruction.right))
				spill_count = spill_count + 1
		elif isinstance(instruction, IfStmt):
			then, then_spill_count = generate_spill_code(instruction.then, spilled, spill_count)
			else_, else_spill_count = generate_spill_code(instruction.else_, spilled, spill_count+then_spill_count)
			spill_count = spill_count + then_spill_count + else_spill_count
			generated_code.append(IfStmt(then,instruction.test, else_))
		elif isinstance(instruction, Addl)         \
		   and isinstance(instruction.left, Name)  \
		   and (instruction.right.name in spilled.keys()) \
		   and (instruction.left.name in spilled.keys()):
				spill_var = get_spill_var_name()
				generated_code.append(Movl(instruction.left, Name(spill_var)))
				generated_code.append(Addl(Name(spill_var), instruction.right))
				spill_count = spill_count + 1
		else:
			generated_code.append(instruction)
	return (generated_code, spill_count)
