

import compiler
import sys, getopt, os
from x86_ast import *
from compiler.ast import *
from explicate_ast import *

INSTRUCTIONS = 0
LIVE_VARS    = 1

def get_variables(instructions):
	interference_graph = {"%eax" : set(), "%ebx" : set(), "%ecx" : set(), "%edx" : set(), "%esi" : set(), "%edi": set()}
	for instruction in instructions:
		if isinstance(instruction, Movl):
			if isinstance(instruction.left, Name):
				interference_graph[instruction.left.name] = set()
			if isinstance(instruction.right, Name):
				interference_graph[instruction.right.name] = set()
		elif isinstance(instruction, IfStmt):
			then = get_variables(instruction.then)
                        for var in then.keys():
                            interference_graph[var] = set()
			else_ = get_variables(instruction.else_)
                        for var in else_.keys():
                            interference_graph[var] = set()
			interference_graph[instruction.test.name] = set()
		elif isinstance(instruction, Addl):
			if isinstance(instruction.left, Name):
				interference_graph[instruction.left.name] = set()
			if isinstance(instruction.right, Name):
				interference_graph[instruction.right.name] = set()
		elif isinstance(instruction, Negl):
			if isinstance(instruction.node, Name):
				interference_graph[instruction.node.name] = set()
		elif isinstance(instruction, Popl):
			if isinstance(instruction.node, Name):
				interference_graph[instruction.node.name] = set()
		elif isinstance(instruction, Pushl):
			if isinstance(instruction.node, Name):
				if "func$" not in instruction.node.name:
					interference_graph[instruction.node.name] = set()
		elif isinstance(instruction, Compare):
			if isinstance(instruction.node.expr, Name):
				interference_graph[instruction.node.expr.name] = set()
			if isinstance(instruction.node.ops[0][1], Name):
				interference_graph[instruction.node.ops[0][1].name] = set()
		elif isinstance(instruction, While):
			body = get_variables(instruction.body)
			for var in body:
				interference_graph[var] = set()
			test = get_variables(instruction.test[1])
			for var in test:
				interference_graph[var] = set()
			if isinstance(instruction.test[0], Name):
				interference_graph[instruction.test[0].name] = set()
	if "%esp" in interference_graph.keys():
		del interference_graph["%esp"]
	if "%ebp" in interference_graph.keys():
		del interference_graph["%ebp"]
	return interference_graph

def remove_ints(graph):
	for key in graph.keys():
		if isinstance(key, int):
			del graph[key]
		else:
			graph[key] = set([e for e in graph[key] if not isinstance(e, int)])
	return graph

def generate_rig(inst_live_pair):
	interference_graph = get_variables([list(e) for e in zip(*inst_live_pair)][INSTRUCTIONS])
	#print "Pair"

	for pair in inst_live_pair:
		instruction = pair[INSTRUCTIONS]
		live_vars   = pair[LIVE_VARS]
		if isinstance(instruction, Movl) or isinstance(instruction, Addl):
			right_name = instruction.right.name
			left_name  = ''
			if isinstance(instruction.left, Name):
				left_name = instruction.left.name
			for var in live_vars:
				#if var not in [right_name, left_name]:
					if right_name not in ["%esp", "%ebp"]:
						interference_graph[right_name].add(var)
						interference_graph[var].add(right_name)
			if left_name is not '':
					for var in live_vars:
						#if var not in [right_name, left_name]:
							if right_name not in ["%esp", "%ebp"]:
								interference_graph[left_name].add(var)
								interference_graph[var].add(left_name)
			for var1 in live_vars:
				for var2 in live_vars:
					if var1 != var2:
						#print "Make if edges"
						interference_graph[var1].add(var2)
						interference_graph[var2].add(var1)
		elif isinstance(instruction, IfStmt) or isinstance(instruction, While):
			for var1 in live_vars:
				for var2 in live_vars:
					if var1 != var2:
						interference_graph[var1].add(var2)
						interference_graph[var2].add(var1)
		elif isinstance(instruction, Call) or isinstance(instruction, PrintX86):
			for var in live_vars:
				interference_graph[var] = interference_graph[var] | set(["%eax", "%edx", "%ecx"])
				interference_graph["%eax"].add(var)
				interference_graph["%edx"].add(var)
				interference_graph["%ecx"].add(var)
		elif isinstance(instruction, Negl):
			name = ""
			if isinstance(instruction.node, Name):
				name = instruction.node.name

				for var in live_vars:
					if var != name:
						interference_graph[name].add(var)
						interference_graph[var].add(name)
	return remove_ints(interference_graph)
