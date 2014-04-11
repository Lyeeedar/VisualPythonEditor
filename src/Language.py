'''
Created on 29 Jan 2014

@author: Philip
'''

import Queue

class Program:
    def __init__(self):
        self.methods = []
        
    def addMethod(self, method):
        if not method in self.methods:
            self.methods.append(method)

class Method:
    def __init__(self, name):
        self.name = name
        self.inputs = []
        self.nodes = []
        self.outputs = []
        self.setNumInputs(1)
        self.setNumOutputs(1)
        
    def setNumInputs(self, num, baseName="Input"):
        prev = self.inputs
        self.inputs = [""] * num
        for i in range(num):
            if i < len(prev) :
                self.inputs[i] = prev[i]
            else :
                self.inputs[i] = baseName+str(i)
            
    def setNumOutputs(self, num, baseName="Output"):
        prev = self.outputs
        self.outputs = [""] * num
        for i in range(num):
            if i < len(prev) :
                self.outputs[i] = prev[i]
            else :
                self.outputs[i] = baseName+str(i)
        
    def addNode(self, node):
        self.nodes.append(node)
            
    def compile(self):
        for node in self.nodes:
            node.reset()
        
        processList = Queue.Queue() 
        data = {}
        data["Queue"] = processList
        data["Return"] = {}
        data["Code"] = []
        
        for node in self.nodes:
            if isinstance(node, TerminalNode):
                processList.put_nowait(node)
        
        while not processList.empty() :
            node = processList.get_nowait()
            node.process(data)
        
        data["Code"].sort(key=lambda tup: tup[0], reverse = True)
        
        method = "def "+self.name+"("
        first = True
        for input in self.inputs:
            if first:
                first = False
            else:
                method += ", "
            method += input
        method+="):"
        
        for line in data["Code"] :
            method += "\n\t"+line[1]
            
        method += "\n\treturn ("
        first = True
        for key in data["Return"].keys():
            if first:
                first = False
            else:
                method += ", "
            method += data["Return"][key]
        method += ")"
            
        print method
    
class Node:
    def __init__(self, name):
        self.reset()
        
        self.name = name
        self.links = {}
        self.setNumLinks(1, name)
    
    def reset(self):
        self.added = False
        self.priority = 0
    
    def removeLink(self, name):
        self.links[name] = ()

    def addLink(self, name, node, nodename):
        self.links[name] = (node, nodename)
        
    def setNumLinks(self, num, baseName):
        prevLinks = self.links
        keys = prevLinks.keys()
        self.links = {}
        for i in range(num):
            if i < len(keys) :
                self.links[keys[i]] = prevLinks[keys[i]]
            else :
                self.links[baseName+str(i)] = ()

class StartNode(Node):
    pass
class TerminalNode(Node):
    pass
            
class ArgumentNode(StartNode):
    def __init__(self):
        Node.__init__(self, "Method Input")
    
    def set(self, args):
        self.links = {}
        for arg in args:
            self.links[arg] = ()
    
    def process(self, data):    
        pass
    
class OutputNode(TerminalNode):
    def __init__(self):
        Node.__init__(self, "Method Output")
    
    def set(self, outs):
        self.links = {}
        for out in outs:
            self.links[out] = ()
    
    def process(self, data):
        # Build argument string and queue

        for key in self.links.keys() :
            
            if len(self.links[key]) == 0 :
                continue
            
            (node, nodename) = self.links[key]
            
            # Queue if needed
            if not node.added:
                data["Queue"].put_nowait(node)
                node.added = True
            if self.priority+1 > node.priority :
                node.priority = self.priority+1
                
            data["Return"][key] = nodename
               
class MethodNode(Node):
    def __init__(self, method):
        Node.__init__(self, method.name)
        self.method = method
        self.update()
        
    def update(self):
        self.links = {}
        for key in self.method.inputs :
            self.links[key] = {}
            
        self.outputs = []
        for key in self.method.outputs :
            self.outputs.append(key)
        
    def process(self, data):
        # Build argument string and queue
        string = "("
        first = True
        for key in self.outputs :
            if not first :
                string += ", "
            else :
                first = False
            string += key
            
        string += ") = " + self.method.name + "("
        
        first = True
        for key in self.links.keys() :
            (node, nodename) = self.links[key]
            if not first :
                string += ", "
            else :
                first = False
            string += nodename
            
            # Queue if needed
            if not node.added :
                data["Queue"].put_nowait(node)
                node.added = True
            if self.priority+1 > node.priority :
                node.priority = self.priority+1
        
        string += ")"
        
        data["Code"].append((self.priority, string))

def createPassThroughMethod(name, num):
    method = Method(name)
    method.setNumInputs(num)
    method.setNumOutputs(num)
    
    argNode = ArgumentNode()
    argNode.set(method.inputs)
    
    outNode = OutputNode()
    outNode.set(method.outputs)
    
    for i in range(num) :
        outNode.addLink(outNode.links.keys()[i], argNode, argNode.links.keys()[i])
        
    method.addNode(argNode)
    method.addNode(outNode)
        
    return method

def createNStepMethod(name, num, n):
    method = Method(name)
    method.setNumInputs(num)
    method.setNumOutputs(num)
    
    current = None
    for i in range(n) :
        nc = MethodNode(createPassThroughMethod(name+str(i), num))
        if current == None :
            for i in range(num) :
                nc.addLink(nc.links.keys()[i], method.input, method.input.links.keys()[i])
        else :
            for i in range(num) :
                nc.addLink(nc.links.keys()[i], current, current.outputs[i])
                
        current = nc
        method.addNode(nc)
                
    for i in range(num) :
        method.output.addLink(method.output.links.keys()[i], current, current.outputs[i])
    
    return method

method = createPassThroughMethod("TestMethod", 2)
method.compile()







