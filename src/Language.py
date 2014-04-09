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
        self.input = InOutNode("Input")
        self.nodes = []
        self.output = InOutNode("Output")
        
    def setNumInputs(self, num, baseName="Input"):
        self.input.setNumLinks(num, baseName)
            
    def setNumOutputs(self, num, baseName="Output"):
        self.output.setNumLinks(num, baseName)
        
    def addNode(self, node):
        self.nodes.append(node)
            
    def compile(self):
        
        self.input.reset()
        self.input.priority = len(self.nodes)+10
        self.output.reset()
        for node in self.nodes:
            node.reset()
        
        processList = Queue.Queue() 
        lines = []
        
        lines.append((0, self.output.processAsOutput(processList)))
        
        while not processList.empty() :
            node = processList.get_nowait()
            lines.append((node.priority, node.process(processList)))
        
        lines.sort(key=lambda tup: tup[0], reverse = True)
        
        method = "def "+self.name
        
        for line in lines :
            method += line[1]+"\n\t"
            
        print method
        
class InOutNode:
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
             
    def process(self, queue):
        return self.processAsInput()
                
    def processAsInput(self):
        # Build argument string
        string = "("
        first = True
        for key in self.links.keys() :
            if not first :
                string += ", "
            else :
                first = False
            string += key
        string += "):"
        
        return string
    
    def processAsOutput(self, queue):
        # Build argument string and queue
        string = "return ("
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
                queue.put_nowait(node)
                node.added = True
            if self.priority+1 > node.priority :
                node.priority = self.priority+1
            
        string += ")"
        
        return string
        
        
class MethodNode:
    def __init__(self, method):
        self.reset()
        
        self.method = method
        self.links = {}
        self.outputs = {}
        
        self.update()

    def reset(self):
        self.added = False
        self.priority = 0
        
    def update(self):
        self.links = {}
        for key in self.method.input.links.keys() :
            self.links[key] = {}
            
        self.outputs = []
        for key in self.method.output.links.keys() :
            self.outputs.append(key)
        
    def setNumInputs(self, num, baseName) :
        prevLinks = self.links
        keys = prevLinks.keys()
        self.links = {}
        for i in range(num):
            if i < len(keys) :
                self.links[keys[i]] = prevLinks[keys[i]]
            else :
                self.links[baseName+i] = ()
                
    def setNumOutputs(self, num, baseName) :
        prevLinks = self.outputs
        keys = prevLinks.keys()
        self.outputs = {}
        for i in range(num):
            if i < len(keys) :
                self.outputs[keys[i]] = prevLinks[keys[i]]
            else :
                self.outputs[baseName+i] = None
                
    def removeLink(self, name):
        self.links[name] = ()

    def addLink(self, name, node, nodename):
        self.links[name] = (node, nodename)
        
    def process(self, queue):
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
                queue.put_nowait(node)
                node.added = True
            if self.priority+1 > node.priority :
                node.priority = self.priority+1
        
        string += ")"
        
        return string

def createPassThroughMethod(name, num):
    method = Method(name)
    method.setNumInputs(num)
    method.setNumOutputs(num)
    
    for i in range(num) :
        method.output.addLink(method.output.links.keys()[i], method.input, method.input.links.keys()[i])
        
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

method = createNStepMethod("TestMethod", 2, 2)
method.compile()







