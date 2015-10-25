#!/usr/bin/python

import compiler
import sys, getopt, os
from x86_ast import *
from compiler.ast import *
from liveness_analysis import *
from generate_rig import *
from color_graph import *
from generate_spill_code import *
from flatten import *
from translate_to_x86 import *
from pretty_print import *
from explicate_ast import *
from explicate import *
from remove_ifstmts import *
from uniquify import *
from freevars import *
from apply_freevars import *
from heapify import *
from closure_conversion import *
from optimize_pass import *
from local_vars import *

# meaningfully named constants
TEMP_COUNT = 0
ATOMIC     = 0
BINDINGS   = 1

# program: a list of pretty x86 instructions
# fileName: name of the file to write to
def writeFile(program, fileName):
	outFile = open(fileName, "a+")
	for line in program:
		outFile.write(line + "\n")
	outFile.close()

def merge_dict(d1, d2):
	"""Merge d2 to d1"""
	for k in d2.keys():
		d1[k] = d2[k]
	return d1

def main(argv):
    inputFile = str(sys.argv[-1])
    assemblyFile = inputFile[:-2] + "s"

    mod = compiler.parseFile(inputFile)
    optimized_ast = optimize(mod)

    uniquify = uniquify_pass(optimized_ast)
    explicate = explicate_ast(uniquify)
    mappings = apply_free_vars(explicate, {})

    heapified = heapify_ast(explicate, mappings)
    closure_pass = create_closure(heapified)

    flatExprs = flatten_ast(Stmt(closure_pass[0].nodes + closure_pass[1]))
   
    func_code_pair = translate_to_x86(flatExprs)

    for func in func_code_pair.keys():
	x86 = func_code_pair[func][0]
        pair = liveness_analysis(x86, set([]))
        rig = generate_rig(pair)
        mapping, spilled = color_graph(rig, None)
    
        spill_count = 0
        if len(spilled) > 0:
        	x86, spill_count = generate_spill_code(x86, spilled, spill_count)
    #iterations = 0
	if spill_count > 0:
	    pair = liveness_analysis(x86, set([]))
	    rig = generate_rig(pair)
	    mapping, new_spilled = color_graph(rig, spilled)
	    spilled = merge_dict(spilled, new_spilled)
	    x86, spill_count = generate_spill_code(x86, spilled, spill_count)
        # iterations +=1
        #if iterations == 3:
        #    break
    
        x86 = remove_structured_code(x86)
	
        func_code_pair[func] = [x86, len(spilled), mapping, func_code_pair[func][1]]
    
    for func in func_code_pair.keys():
        writeFile(prettyPrint(func, func_code_pair[func][0], func_code_pair[func][1], func_code_pair[func][2], func_code_pair[func][3]), assemblyFile)

if __name__ == "__main__":
	main(sys.argv[1:])
