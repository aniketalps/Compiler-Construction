class livevar:
  def __init__(self,final_list):
    self.final_list = final_list
    self.read = []
    self.write = []
    self.live_after = []
    self.live_before = []
    self.count = 0
    for ct in range(0,10000):
      self.live_after.append([])
      self.live_before.append([])
    
  def liveness(self):
    a = len(self.final_list)
    for i in range(a-1,-1,-1):
      if self.final_list[i].startswith("movl"):
	if "$" in self.final_list[i]:
	  rw0 = self.final_list[i].split(' ')
          rw1 = rw0[1].split(',',1)
	  self.write.append(rw1[1])
	  if self.count != 0:
	    self.live_after[i].extend(self.live_before[i+1])
	  x = (list((set(map(tuple,self.live_after[i])) - set(map(tuple,self.write))) | set(map(tuple,self.read))))
	  for data in x:
	    self.live_before[i].append(''.join(data))
        
	else:
	  rw0 = self.final_list[i].split(' ',1)
          rw1 = rw0[1].split(',',1)
	  rw2 = rw1[0].strip(',')
	  self.read.append(rw2)
	  self.write.append(rw1[1])
	  if self.count != 0:
	    self.live_after[i].extend(self.live_before[i+1])
	  x = (list((set(map(tuple,self.live_after[i])) - set(map(tuple,self.write))) | set(map(tuple,self.read))))
	  for data in x:
	    self.live_before[i].append(''.join(data))
        del self.read[:]
        del self.write[:]
	self.count += 1

      elif self.final_list[i].startswith("addl"):
	if "$" in self.final_list[i]:
	  rw0 = self.final_list[i].split(' ')
          rw1 = rw0[1].split(',',1)
	  self.write.append(rw1[1])
	  if self.count != 0:
	    self.live_after[i].extend(self.live_before[i+1])
	  x = (list((set(map(tuple,self.live_after[i])) - set(map(tuple,self.write))) | set(map(tuple,self.read))))
	  for data in x:
	    self.live_before[i].append(''.join(data))
	
	else:        
	  rw0 = self.final_list[i].split(' ')
          rw1 = rw0[1].split(',',1)
	  self.read.append(rw1[0])
	  self.read.append(rw1[0])
	  self.write.append(rw1[1])
	  if self.count != 0:
	    self.live_after[i].extend(self.live_before[i+1])
	  x = (list((set(map(tuple,self.live_after[i])) - set(map(tuple,self.write))) | set(map(tuple,self.read))))
	  for data in x:
	    self.live_before[i].append(''.join(data))
        del self.read[:]
        del self.write[:]
	self.count += 1
      
      elif self.final_list[i].startswith("negl") or self.final_list[i].startswith("pushl"):
	rw0 = self.final_list[i].split(' ')
	self.write.append(rw0[1])
	if self.count != 0:
	  self.live_after[i].extend(self.live_before[i+1])
	  x = (list((set(map(tuple,self.live_after[i])) - set(map(tuple,self.write))) | set(map(tuple,self.read))))
	  for data in x:
	    self.live_before[i].append(''.join(data))
	else:
	    self.live_before[i].append(rw0[1])
        del self.read[:]
        del self.write[:]
	self.count += 1
	
      elif self.final_list[i].startswith("call"):
        self.read.append('tmpreg')
	self.write.append('tmpreg')
	if self.count != 0:
	  self.live_after[i].extend(self.live_before[i+1])
	x = (list((set(map(tuple,self.live_after[i])) - set(map(tuple,self.write))) | set(map(tuple,self.read))))
	for data in x:
	  self.live_before[i].append(''.join(data))
	del self.read[:]
        del self.write[:]
	self.count += 1


class interference:
  def __init__(self,final_list,lbefore,lafter):
    self.final_list = final_list
    self.lbefore = lbefore
    self.lafter = lafter
    self.inter_dict = {}
    self.templist = []
  
  def generate_graph(self):
    #self.inter_dict = defaultdict(list)
    for i in range(0,len(self.final_list)):
      if self.final_list[i].startswith("movl"):
        #print i
        rw0 = self.final_list[i].split(' ')
        rw1 = rw0[1].split(',',1)
	rw2 = rw1[1].strip(',')
	for l in range(0,len(self.lafter[i])):
	 if '240' not in rw1[1]:
	   if rw1[1] != '%eax' or rw2[0] != '%eax':
	    if self.lafter[i][l] != rw1[1] or self.lafter[i][l] != rw2[0]:
              if rw1[1] not in self.inter_dict.keys():
	        if rw1[1] != self.lafter[i][l]:
      	          self.inter_dict[rw1[1]] = [(self.lafter[i][l])]
	        if self.lafter[i][l] not in self.inter_dict.keys():
	          self.inter_dict[(self.lafter[i][l])] = [rw1[1]]
	        else:
	          self.inter_dict[(self.lafter[i][l])] += [rw1[1]]
	      else:
	        if rw1[1] != self.lafter[i][l]:
	          self.inter_dict[rw1[1]] += [(self.lafter[i][l])]
                if self.lafter[i][l] not in self.inter_dict.keys():
	          self.inter_dict[(self.lafter[i][l])] = [rw1[1]]
	        else:
	          self.inter_dict[(self.lafter[i][l])] += [rw1[1]]
	 

      elif self.final_list[i].startswith("addl"):
        #print i
	rw0 = self.final_list[i].split(' ')
        rw1 = rw0[1].split(',',1)
	for l in range(0,len(self.lafter[i])):
	 if rw1[1] != '%eax' or rw2[0] != '%eax':
	  if self.lafter[i][l] != rw1[1]:
	    if l == 0:
	      self.inter_dict[rw1[1]] = [(self.lafter[i][l])]
#	      self.inter_dict[(self.lafter[i][l])] = rw1[1]
	    else:
	      self.inter_dict[rw1[1]] += [(self.lafter[i][l])]
	     # self.inter_dict[(self.lafter[i][l])] += [rw1[1]]

      elif self.final_list[i].startswith("call"):
          #print i
	  rw0 = self.final_list[i].split(' ')
	  for l in range(0,len(self.lafter[i])):
	    self.inter_dict['callertmp'] = self.lafter[i] + ['eax','ecx','edx']

      elif self.final_list[i].startswith("negl"):
	  rw0 = self.final_list[i].split(' ')
	  for l in range(0,len(self.lafter[i])):
	    if rw0[1] in self.lafter[i]:
	      self.inter_dict[rw0[1]] = self.lafter[i]
	    else:
	      self.inter_dict[rw0[1]] += self.lafter[i]
      
    for k,v in self.inter_dict.items():
	if 'tmpreg' not in v:
	  self.inter_dict[k] += (['tmpreg'])

#Graph coloring algorithm

class graphcolor:
  def __init__(self,inter_graph):
    self.graph = inter_graph
    self.color_vector = ['%ebx','%ecx','%edx','%esp','%edi','%esi']
    self.reg_assign = {}
    self.reg_count = 0
    self.reg_dealloc = []
    self.var_count1 = 4
    #for x in range(0,1):
     # self.reg_dealloc.append([])
    self.reg_set = []
  
  def regalloc(self):
    #index = "tmp0"
    
    while len(self.graph) != 0:
      hsat = 0
      
      for k,v in self.graph.items():
        if len(self.graph[k]) > hsat:
          hsat = len(self.graph[k])
	  index = k

      self.reg_assign['tmpreg'] = '%eax'
      
      for i in self.graph[index]:
	if index == 'callertmp':
          if '%eax' not in self.reg_dealloc:
	    self.reg_dealloc.append('%eax')
	    self.reg_dealloc.append('%ecx')
	    self.reg_dealloc.append('%edx')
        for k1,v1 in self.reg_assign.items():
	  if self.reg_count != 0:
	    if [i] == [k1]:
	      self.reg_dealloc.append(v1)

	if self.reg_count != 0: 
	  self.reg_set = (list(set(self.color_vector) - set(self.reg_dealloc)))
	elif self.reg_count == 0:
	  if index == 'callertmp':
	    self.reg_set = (list(set(self.color_vector) - set(self.reg_dealloc)))
	      
      
#Register assignment
      if len(self.reg_set) == 0 and index != 'callertmp':
	if index != 'tmpreg':
	  self.reg_assign[index] = self.color_vector[0]
      else:
	if index != 'tmpreg': 
	   if len(self.reg_set) == 1:
	     self.reg_assign[index] = '-'+str(self.var_count1)+'(%ebp)'
	     self.var_count1 += 4
	   else:
             self.reg_assign[index] = self.reg_set[0]

      self.reg_count += 1
      del self.graph[index]
      del self.reg_set[:]
      del self.reg_dealloc[:]

