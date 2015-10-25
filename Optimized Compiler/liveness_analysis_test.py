#!/usr/bin/python

import compiler
import sys, getopt, os
from x86_ast import *
from compiler.ast import *


RESERVE = set(['%esp', '%ebp'])

# input: list of x86 AST nodes
# return: a list of sets indicating
#         that variables are alive at
#         a given instruction
def liveness_analysis(n):
    live_variables = [set()]
    instructions = []
    n.reverse()

    for node in n:
        if isinstance(node, Pushl):
            live_variables.append(live_variables[-1])
            instructions.append(node)
        elif isinstance(node, Popl):
            write = set()
            if isinstance(node.node, Name) and node.node not in RESERVE:
                write.add(node.node.name)
            live_variables.append(live_variables[-1])# - write) # | set([node.node.name]))
            instructions.append(node)
        elif isinstance(node, PrintX86):
            read = set()
            if isinstance(node.node, Name) and node.node not in RESERVE:
                read.add(node.node.name)
            live_variables.append(live_variables[-1])# | read)
            instructions.append(node)
        elif isinstance(node, Movl):
            read = set()
            if isinstance(node.left, Name) and node.left not in RESERVE:
                read.add(node.left.name)
            #create write set
            write = set()
            if node.right.name not in RESERVE:
				write.add(node.right.name)
            l_before = (live_variables[-1] - write) | read
            live_variables.append(l_before)
            instructions.append(node)
        elif isinstance(node, Addl):
            read = set()
            write = set()
            if isinstance(node.left, Name):
                read.add(node.left.name)
            #create write set
            if node.right.name not in RESERVE:
                write.add(node.right.name)
            l_before = (live_variables[-1] | write) | read
            live_variables.append(l_before)
            instructions.append(node)
        elif isinstance(node, Call):
            instructions.append(node)
            live_variables.append(live_variables[-1])
        #elif isinstance(node, PrintX86):
        #    instructions.append(node)
        #    live_variables.append(live_variables[-1])
        elif isinstance(node, Negl):
            if isinstance(node.node, Name):
                live_variables.append(live_variables[-1] | set([node.node.name]))
            else:
                live_variables.append(live_variables[-1])
            instructions.append(node)
        elif isinstance(node, NOOP):
            live_variables.append(live_variables[-1])
            instructions.append(node)
        else:
            raise Exception('Error in liveness analysis: unrecognized x86 AST node')
    result = zip(instructions, live_variables)
    result.reverse()
    for r in result:
        print r
        print
    n.reverse()
    return result
