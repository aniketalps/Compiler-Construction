#!/usr/bin/python

#Recursion over ASTs

from compiler.ast import *
import p0regalloc
from sets import Set
import sys

varCount_g = 4
count_g = 0
varLkp_g = {}
counter_g = 0
li_final_g = []
tmp_g = 0

class p0flatast:
  global tmp_g
  def __init__(self, ast):
    self.tmp = 0
    self.ast = ast
    self.flat = []

  def p0ast_flatten(self,ast):
	if isinstance(ast, Module):
	  self.p0ast_flatten(ast.node)
	elif isinstance(ast,Stmt):
	  for c in ast.nodes:
	    self.p0ast_flatten(c)
	elif isinstance(ast,Printnl):
	  try:
            child = self.p0ast_flatten(ast.nodes[0])
            self.flat.append(Printnl([child],None))
	  except IndexError:
	    print "IndexError"
	elif isinstance(ast, Assign):
  	  assVal = self.p0ast_flatten(ast.expr)
          for node in ast.nodes:
            assName = self.p0ast_flatten(node)
            self.flat.append(Assign(assName, assVal))
            self.tmp += 1
          return assVal
	elif isinstance(ast,AssName):
          return Name(ast.name)
        elif isinstance(ast,Discard):
          child = self.p0ast_flatten(ast.expr)
          if isinstance(child,CallFunc):
            self.flat.append(child)
        elif isinstance(ast,Const):
          return ast
        elif isinstance(ast,Name):
          return ast
	elif isinstance(ast, UnarySub):
	  expr = self.p0ast_flatten(ast.expr)
          tmpVar = Name('tmp'+`self.tmp`)
          self.flat.append(Assign(tmpVar, UnarySub(expr)))
          self.tmp += 1
          return tmpVar
	elif isinstance(ast, Add):
	  left = self.p0ast_flatten(ast.left)
	  right = self.p0ast_flatten(ast.right)
	  if isinstance(left,Const) and isinstance(right,Const):
            return Const(left.value+right.value)
        
          tmpVar = Name('tmp'+`self.tmp`)
          self.flat.append(Assign(tmpVar, Add((left,right))))
          self.tmp += 1
          return tmpVar
	elif isinstance(ast,CallFunc):
          newTmp = Name('tmp'+`self.tmp`)
          self.flat.append(Assign(newTmp, ast))
          self.tmp += 1
          return newTmp

class pyt_to_x86:
  def __init__(self, flatAst):
    self.flatAst = flatAst
    global varCount_g
    global count_g
    global varLkp_g
    global counter_g 
    global li_final_g
    self.dict = { "node.l":"movl $arg,tmpreg",
		  "node.add":"addl $arg,tmpreg",
	          "node.addstack":"addl $varcount,tmpreg",
  		  "node.postadd":"movl tmpreg,$varcount",
		  "node.unarysub":"negl tmpreg",
		  "node.print":"pushl tmpreg \ncall print_int_nl",
		  "node.assignval":"movl $str,$varcount",
		  #"node.assign":"$varcount",
		  "node.get":"movl $varcount,tmpreg",
		  "input":"movl %eax,-$svarcount(%ebp) \ncall input" }


    self.pre_list = [".globl main","main:","pushl %ebp","movl %esp,%ebp","subl $var,%esp"]
    self.post_list = ["addl $var,%esp","movl $0,%eax","leave","ret"]
    
    self.finaloutput = []
    for x in range(0,4000):
      self.finaloutput.append([])
    self.varCount = 1
    self.count = 0
    self.varLkp = {}
    self.counter = 0
    self.li_final = []
    
  def flattox86(self):
    for c in self.flatAst:
      if isinstance(c, Assign):
        self.convertLine(c.expr, c.nodes.name)
      elif isinstance(c, Printnl):
	if isinstance(c.nodes[0], Const):
	    arg = c.nodes[0].value
	    self.finaloutput[self.count].append(arg)
	    self.finaloutput[self.count].append("node.l")
	    self.count += 1
	    self.finaloutput[self.count].append("0")
            self.finaloutput[self.count].append("node.print")
	    self.count += 1
	elif isinstance(c.nodes[0], Name):
	    if c.nodes[0].name not in self.varLkp:
	       self.varLkp[c.nodes[0].name] = self.varCount
	       self.varCount += 1
            arg = self.varLkp[c.nodes[0].name]
	    self.finaloutput[self.count].append(arg)
	    self.finaloutput[self.count].append("node.get")
	    self.count += 1
	    self.finaloutput[self.count].append("0")
            self.finaloutput[self.count].append("node.print")
	    self.count += 1
	else:
	  try:
	    self.finaloutput[self.count].append(c.nodes[0].value)
	    self.finaloutput[self.count].append("node.assignval")
	    self.finaloutput[self.count].append(self.varCount)
	    self.count += 1
	   # self.finaloutput[self.count].append(self.varCount)
	   # self.finaloutput[self.count].append("node.assign")
	   # self.count += 1
	    self.finaloutput[self.count].append(self.varCount)
            self.finaloutput[self.count].append("node.get")
            self.count += 1
	    self.finaloutput[self.count].append("0")
            self.finaloutput[self.count].append("node.print")
	    self.count += 1
	  except:
	    self.finaloutput[self.count].append("0")
            self.finaloutput[self.count].append("node.print")
	    self.count += 1

  def convertLine(self,c,tmpName):
      if isinstance(c,Add):
	if isinstance(c.left, Const):
	    arg = c.left.value
	    self.finaloutput[self.count].append(arg)
	    self.finaloutput[self.count].append("node.l")
	    self.count += 1
	elif isinstance(c.left, Name):
	    if c.left.name not in self.varLkp:
	       self.varLkp[c.left.name] = self.varCount
	       self.varCount += 1
            arg = self.varLkp[c.left.name]
	    self.finaloutput[self.count].append(arg)
	    self.finaloutput[self.count].append("node.get")
	    self.count += 1
	if isinstance(c.right, Const):
	    arg = c.right.value
	    self.finaloutput[self.count].append(arg)
	    self.finaloutput[self.count].append("node.add")
	    self.count += 1
	    self.finaloutput[self.count].append(self.varCount)
	    self.finaloutput[self.count].append("node.postadd")
	    self.count += 1
	elif isinstance(c.right, Name):
	    if c.right.name not in self.varLkp:
	       self.varLkp[c.right.name] = self.varCount
	       self.varCount += 1
	    if tmpName not in self.varLkp:
	       self.varLkp[tmpName] = self.varCount
	       #self.varCount += 1
	    arg = self.varLkp[c.right.name]
  	    self.finaloutput[self.count].append(arg)
	    self.finaloutput[self.count].append("node.addstack")
	    self.count += 1
	    self.finaloutput[self.count].append(self.varCount)
	    self.finaloutput[self.count].append("node.postadd")
	    self.count += 1
	    self.varCount += 1   #

      elif isinstance(c,Const):
	if tmpName not in self.varLkp:
	  self.varLkp[tmpName] = self.varCount
	  self.varCount += 1
	arg = self.varLkp[tmpName]
	self.finaloutput[self.count].append(c.value)
	self.finaloutput[self.count].append("node.assignval")
	self.finaloutput[self.count].append(arg)
	self.count += 1
	#self.finaloutput[self.count].append(arg)
	#self.finaloutput[self.count].append("node.assign")
	#self.count += 1

      elif isinstance(c,Name):
	if c.name not in self.varLkp:
	    self.varLkp[c.name] = self.varCount
	    self.varCount += 1
	arg = self.varLkp[c.name]
	self.finaloutput[self.count].append(arg)
	self.finaloutput[self.count].append("node.get")
	self.count += 1
	if tmpName not in self.varLkp:
	  self.varLkp[tmpName] = self.varCount
	  self.varCount += 1
	arg = self.varLkp[tmpName]
	self.finaloutput[self.count].append(arg)
	self.finaloutput[self.count].append("node.postadd")
	self.count += 1 

      elif isinstance(c,UnarySub):
	if isinstance(c.expr, Name):
	  if c.expr.name not in self.varLkp:
	    self.varLkp[c.expr.name] = self.varCount
	    self.varCount += 1
	  arg = self.varLkp[c.expr.name]
	  self.finaloutput[self.count].append(arg)
	  self.finaloutput[self.count].append("node.get")
	  self.count += 1
	  self.finaloutput[self.count].append("0")
	  self.finaloutput[self.count].append("node.unarysub")
	  self.count += 1
	  if tmpName not in self.varLkp:
	    self.varLkp[tmpName] = self.varCount
	    self.varCount += 1
	  arg = self.varLkp[tmpName]
	  self.finaloutput[self.count].append(arg)
	  self.finaloutput[self.count].append("node.postadd")
	  self.count += 1
           
	elif isinstance(c.expr,Const):
	  self.finaloutput[self.count].append(c.expr.value)
	  self.finaloutput[self.count].append("node.assignval")
	  #self.count += 1
	  if tmpName not in self.varLkp:
	    self.varLkp[tmpName] = self.varCount
	    self.varCount += 1
	  arg = self.varLkp[tmpName]
  	  self.finaloutput[self.count].append(arg)
	  self.count += 1
	  #self.finaloutput[self.count].append("node.assign")
	  #self.count += 1
	  arg = self.varLkp[tmpName]
	  self.finaloutput[self.count].append(arg)
	  self.finaloutput[self.count].append("node.get")
	  self.count += 1
	  self.finaloutput[self.count].append("0")
	  self.finaloutput[self.count].append("node.unarysub")
	  self.count += 1
	  if tmpName not in self.varLkp:
	    self.varLkp[tmpName] = self.varCount
	    self.varCount += 1
	  arg = self.varLkp[tmpName]
	  self.finaloutput[self.count].append(arg)
	  self.finaloutput[self.count].append("node.postadd")
	  self.count += 1
	  

      elif isinstance(c,CallFunc):
        if tmpName not in self.varLkp:
	    self.varLkp[tmpName] = self.varCount
	    self.varCount += 1
	arg = self.varLkp[tmpName]
	self.finaloutput[self.count].append(arg)
	self.finaloutput[self.count].append("input")
	self.count += 1
	self.finaloutput[self.count].append(arg)
	self.finaloutput[self.count].append("node.postadd")
        self.count += 1
	

  def finalx86(self):

    for y in range(0,len(self.pre_list)):
    	  s1 = self.pre_list[y] 
	  if "$varcount" in s1:
	    s1 = s1.replace("$varcount","$" + str(self.varCount))
	    self.pre_list[y] = s1

    for x in range(0,self.count):
      s = self.dict.get(self.finaloutput[x][1]) 
      if "$arg" in s:
         s = s.replace("$arg","$" + str(self.finaloutput[x][0]))
	 if "$varcount" in s:
	    s = s.replace("$varcount", "tmp"+str(self.finaloutput[x][0]-1))
      elif "$str" in s:
	  s = s.replace("str","$" + str(self.finaloutput[x][0]))
	  if "$varcount" in s:
	    s = s.replace("$varcount", "tmp"+str(self.finaloutput[x][2]-1))
      elif "$varcount" in s and "ebp" not in s:
	 s = s.replace("$varcount", "tmp"+str(self.finaloutput[x][0]-1))
      elif "$svarcount" in s:
	 s = s.replace("$svarcount","240")
     
      self.li_final.append(s)
        

    for z in range(0,len(self.post_list)):
	  s2 = self.post_list[z] 
	  if "$varcount" in s2:
	    s2 = s2.replace("$varcount","$" + "tmp"+str(self.varCount-1))
	    self.post_list[z] = s2



def file_len(fname):
    with open(fname) as fl:
      flen1 = len(fl.readlines())
    return flen1


if __name__ == "__main__":
	import compiler
	from p0regalloc import *
	global varCount_g
        global count_g
        global varLkp_g
        global counter_g 
        global li_final_g
        global tmp_g
	blank_count = 0
	ecx_count = 0
	edx_count = 0
	flag_ecx = 0
	flag_edx = 0
	inp_count = 0
	flen = file_len(sys.argv[1])
	f2 = open(str(sys.argv[1]))
	for linex in f2:
	 if linex.startswith('#'):
          continue
	 ind = linex.find('#')
	 if ind >= 0:
	  linex1 = linex[0:ind-1]
          linex = linex1
	 if linex and (not linex.isspace()):
	  try:
	   ast = compiler.parse(linex.rstrip('\n'))
	   parser = p0flatast(ast)
           parser.p0ast_flatten(parser.ast)
	   flat = pyt_to_x86(parser.flat)
	   flat.flattox86()
	   flat.finalx86()
	   tmp_g = parser.tmp
	   varCount_g = flat.varCount
	   blank_count += 1
	   varLkp_g = flat.varLkp
	   counter_g = flat.counter
	   li_final_g = flat.li_final
	  except SyntaxError:
	   print "Syntax Error"
	
	 for x in range(1,flen):
	  for linex in f2:
	   if linex.startswith('#'):
             continue
	   ind = linex.find('#')
	   if ind >= 0:
	    linex1 = linex[0:ind-1]
            linex = linex1
	   
	   if linex and (not linex.isspace()):
	    try:
	     ast = compiler.parse(linex.rstrip('\n'))
	     parser = p0flatast(ast)
	     parser.tmp = tmp_g
             parser.p0ast_flatten(parser.ast)
	     flat = pyt_to_x86(parser.flat)
	     flat.varCount = varCount_g
	     tmp_g = parser.tmp
	     flat.varLkp = varLkp_g
	     flat.counter = counter_g
	     flat.li_final = li_final_g
	     flat.flattox86()
	     flat.finaloutput
	     flat.finalx86()
	     blank_count += 1
	     varCount_g = flat.varCount
	     varLkp_g = flat.varLkp
	     counter_g = flat.counter
	     li_final_g = flat.li_final
	    except SyntaxError:
	     print "Syntax Error"
	  
	if blank_count == 0:
	     linex = f2.readline()
	     ast = compiler.parse(linex.rstrip('\n'))
	     parser = p0flatast(ast)
             parser.p0ast_flatten(parser.ast)
	     flat = pyt_to_x86(parser.flat)
	     flat.li_final.append("pushl %eax")

# Liveness Analysis
	live = livevar(flat.li_final)
	live.liveness()
	#print live.live_after
	#print live.live_before

# Interference graph

	graph = interference(flat.li_final,live.live_before,live.live_after)
	graph.generate_graph()
	#print graph.inter_dict
	
# Coloring the graph

	color = graphcolor(graph.inter_dict)
	color.regalloc()
	#print color.reg_assign

	#print color.reg_assign.keys()
	for x in range(0,len(flat.li_final)):
	  rw0 = flat.li_final[x].split(' ')
	  rw = rw0[0].split(' ')
          rw1 = rw0[1].split(',',1)

	  if rw[0] == "movl":
	    rw2 = rw1[0].split(',')
	    if '240' not in rw1[1]:
	      if rw1[1] in color.reg_assign.keys():
	          flat.li_final[x] = flat.li_final[x].replace(rw1[1],color.reg_assign[rw1[1]])
	      elif rw1[1] not in color.reg_assign.keys() and "$" not in rw1[1]:
	          flat.li_final[x] = flat.li_final[x].replace(rw1[1],'-200(%ebp)')
	      if rw2[0] in color.reg_assign.keys():
	          flat.li_final[x] = flat.li_final[x].replace(rw2[0],color.reg_assign[rw2[0]])
	      elif rw2[0] not in color.reg_assign.keys() and "$" not in rw2[0]:
	          flat.li_final[x] = flat.li_final[x].replace(rw2[0],'-400(%ebp)')


	  elif rw[0] == "addl":
	    rw2 = rw1[0].split(',')
	    if rw1[1] in color.reg_assign.keys():
	      flat.li_final[x] = flat.li_final[x].replace(rw1[1],color.reg_assign[rw1[1]])
	    elif rw1[1] not in color.reg_assign.keys() and "$" not in rw1[1]:
	      flat.li_final[x] = flat.li_final[x].replace(rw1[1],'-200(%ebp)')
	    if rw2[0] in color.reg_assign.keys():
	      flat.li_final[x] = flat.li_final[x].replace(rw2[0],color.reg_assign[rw2[0]])
	    elif rw2[0] not in color.reg_assign.keys() and "$" not in rw2[0]:
	      flat.li_final[x] = flat.li_final[x].replace(rw2[0],'-400(%ebp)')
	    
	  elif rw[0] == "negl" or rw[0] == "pushl":
	    if rw0[1] in color.reg_assign.keys():
	      flat.li_final[x] = flat.li_final[x].replace(rw0[1],color.reg_assign[rw0[1]])
	 

	for x in range(0,len(flat.li_final)):
	  rw0 = flat.li_final[x].split(' ')
	  rw = rw0[0].split(' ')
          rw1 = rw0[1].split(',',1)

	  if rw[0] == "movl":
	    rw2 = rw1[0].split(',')
	    if "ebp" in rw1[1] and "ebp" in rw2[0]:
	       flat.li_final[x] = "movl " + rw2[0] + "," + "%eax\n" + "movl %eax," + rw1[1]

	  elif rw[0] == "addl":
	    rw2 = rw1[0].split(',')
	    if "ebp" in rw1[1] and "ebp" in rw2[0]:
	       flat.li_final[x] = "movl " + rw2[0] + "," + "%eax\n" + "movl %eax," + rw1[1]

	for x in range(0,len(flat.li_final)):
	    if "ecx" in flat.li_final[x]: 
	      ecx_count += 1
	    elif "edx" in flat.li_final[x]:
	      edx_count += 1
	    elif "input" in flat.li_final[x]:
	      inp_count = 1
	    
	for x in range(0,len(flat.li_final)):
	    if inp_count == 1:
	      if "ecx" in flat.li_final[x]:
	        flat.li_final[x] = flat.li_final[x].replace("%ecx","-"+str(color.var_count1+4)+"(%ebp)")
	        flag_ecx = 1
	    if inp_count == 1:		
	      if "edx" in flat.li_final[x]:
	        flat.li_final[x] = flat.li_final[x].replace("%edx","-"+str(color.var_count1+8)+"(%ebp)")
	        flag_edx = 1
	
	for x in range(0,len(flat.post_list)):
	    if "$var" in flat.post_list[x]:
	      if flag_edx == 1:
	        flat.post_list[x] = flat.post_list[x].replace("var",str(color.var_count1+8))
	      elif flag_ecx == 1:
	        flat.post_list[x] = flat.post_list[x].replace("var",str(color.var_count1+4))
	      else:
	        flat.post_list[x] = flat.post_list[x].replace("var",str(color.var_count1))

	for x in range(0,len(flat.pre_list)):
	    if "$var" in flat.pre_list[x]:
	      if flag_edx == 1:
	        flat.pre_list[x] = flat.pre_list[x].replace("var",str(color.var_count1+8))
	      elif flag_ecx == 1:
	        flat.pre_list[x] = flat.pre_list[x].replace("var",str(color.var_count1+4))
	      else:
	        flat.pre_list[x] = flat.pre_list[x].replace("var",str(color.var_count1))
	
	#write to file
	fin1 = str(sys.argv[1])
        fs = fin1.replace(".py",".s")
	
        f = open(fs, "w")
	for item in flat.pre_list:
	    f.write("%s\n" % (item))
	for item in flat.li_final:
	  if "$$" in item:
	    item = item.replace("$$","$")
	    f.write("%s\n" % (item))	
	  else:
	    f.write("%s\n" % (item))
	for item in flat.post_list:
	    f.write("%s\n" % (item))
	f.close()
