'''
Created on 29 Jan 2014

@author: Philip
'''

import Queue

class Program:
    def __init__(self, name):
        self.methods = []
        self.name = name
        
    def addMethod(self, method):
        if not method in self.methods:
            self.methods.append(method)        

    def checkNameUsed(self, name):
        for method in self.methods:
            if name == method.name:
                return True
        return False            
    def getUnusedName(self):
        name = "Empty_Method"
        while self.checkNameUsed(name):
            name = name + "0"
        return name
    
    def compile(self, mainMethod):
        code = "class " + self.name + ":\n"
        for method in self.methods:
            code += method.compile() + "\n\n"
        code += "program = " + self.name + "()\n"
        code += "program." + mainMethod.name + "()"
        return code

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
    
    def removeNode(self, node):
        self.nodes.remove(node)
    
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
            for key in node.links.keys():
                tuple = node.links[key]
                if len(tuple) == 0:
                    continue
                linked = tuple[0]
                # Queue if needed
                if not linked.added :
                    data["Queue"].put_nowait(linked)
                    linked.added = True
                if node.priority+1 > linked.priority :
                    linked.priority = node.priority+1
        
        data["Code"].sort(key=lambda tup: tup[0], reverse = True)
        
        method = "\tdef "+self.name+"(self"
        for input in self.inputs:
            method += ", "
            method += input
        method+="):"
        
        for line in data["Code"] :
            method += "\n\t\t"+line[1]
        
        if len(data["Return"]) > 0:
            method += "\n\t\treturn ("
            first = True
            for key in data["Return"].keys():
                if first:
                    first = False
                else:
                    method += ", "
                method += data["Return"][key]
            method += ")"
            
        return method
    
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
                
    def update(self):
        pass

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
    
class ValueNode(StartNode):
    def __init__(self, name, value):
        Node.__init__(self, value)
        self.links = {}
        self.links[name] = ()
    
    def set(self, name, value):
        self.name = value
        self.links = {}
        self.links[name] = ()
    
    def process(self, data):    
        code = self.links.keys()[0] + " = " + self.name
        data["Code"].append((self.priority, code))
    
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

class PrintNode(TerminalNode):
    def __init__(self):
        Node.__init__(self, "Print")
        self.links = {}
        self.links["Print"] = ()
        
    def process(self, data):
        code = "print " + self.links["Print"][1]
        data["Code"].append((self.priority, code))
        
class FileWriteNode(TerminalNode):
    def __init__(self):
        Node.__init__(self, "File Write")
        
        self.links = {}
        self.links["Filename"] = ()
        self.links["Contents"] = ()
        
    def process(self, data):
        code = "file = open(" + self.links["Filename"][1] + ", 'w')\n\t\t"
        code += "file.write(" + self.links["Contents"][1] + ")\n\t\t"
        code += "file.close()"
        data["Code"].append((self.priority, code))

class FileReadNode(Node):
    def __init__(self):
        Node.__init__(self, "File Read")
        self.outputs = []
        
        self.links = {}
        self.links["Filename"] = ()
        self.outputs.append("Contents")
    
    def process(self, data):
        code = "file = open(" + self.links["Filename"][1] + ", 'r')\n\t\t"
        code += "Contents = file.read()\n\t\t"
        code += "file.close()"
        data["Code"].append((self.priority, code))
           
class MethodNode(Node):
    def __init__(self, method):
        Node.__init__(self, method.name)
        self.method = method
        self.outputs = []
        self.update()
        
    def update(self):
        self.name = self.method.name
        for key in self.method.inputs :
            if not key in self.links:
                self.links[key] = {}
            
        for key in self.method.outputs:
            if not key in self.outputs:
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

def createTestInputsMethod(name):
    method = Method(name)
    method.setNumInputs(1)
    method.setNumOutputs(3)
    
    argNode = ArgumentNode()
    argNode.set(method.inputs)
    
    outNode = OutputNode()
    outNode.set(method.outputs)
    
    outNode.addLink(outNode.links.keys()[0], argNode, argNode.links.keys()[0])
        
    method.addNode(argNode)
    method.addNode(outNode)
    
    valNode = ValueNode("IntOut", "2")
    outNode.addLink(outNode.links.keys()[1], valNode, valNode.links.keys()[0])
    method.addNode(valNode)
    
    filenameNode = ValueNode("filename", "'test.txt'")
    fileNode = FileReadNode()
    fileNode.addLink(fileNode.links.keys()[0], filenameNode, filenameNode.links.keys()[0])
    outNode.addLink(outNode.links.keys()[2], fileNode, fileNode.outputs[0])
    method.addNode(fileNode)
    method.addNode(filenameNode)
        
    return method

def createTestOutputsMethod(name):
    method = Method(name)
    method.setNumInputs(3)
    method.setNumOutputs(1)
    
    argNode = ArgumentNode()
    argNode.set(method.inputs)
    
    outNode = OutputNode()
    outNode.set(method.outputs)
    
    outNode.addLink(outNode.links.keys()[0], argNode, argNode.links.keys()[0])
        
    method.addNode(argNode)
    method.addNode(outNode)
    
    filenameNode = ValueNode("filename", "'test.txt'")
    fileNode = FileWriteNode()
    fileNode.addLink("Filename", filenameNode, filenameNode.links.keys()[0])
    fileNode.addLink("Contents", argNode, argNode.links.keys()[1])
    method.addNode(fileNode)
    method.addNode(filenameNode)
    
    printNode = PrintNode()
    printNode.addLink(printNode.links.keys()[0], argNode, argNode.links.keys()[2])
    method.addNode(printNode)
        
    return method

if __name__ == "__main__":
    program = Program("TestProgram")
    program.addMethod(createPassThroughMethod("TestMethod1", 2))
    program.addMethod(createTestInputsMethod("TestMethod2"))
    program.addMethod(createTestOutputsMethod("TestMethod3"))
    print program.compile(program.methods[0])
    







