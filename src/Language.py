'''
Created on 29 Jan 2014

@author: Philip
'''

import Queue
import copy

dataClass = \
"""class Data:
    def __init__(self, values, data=None, iteration="Single", orientation="Row"):
        if not hasattr(values, '__iter__'):
            values = [values]
        self.values = values
        self.iteration = iteration
        self.orientation = orientation
        if data != None:
            self.iteration = data.iteration
            self.orientation = data.orientation

    def wrapIndex(self, index):
        if self.iteration == "Single":
            if index >= len(self):
                index = len(self)-1
        elif self.iteration == "Wrapped":
            index = index % (len(self)-1)
        return index    

    def __getitem__(self, key):
        key = self.wrapIndex(key)
        if self.orientation == "Row":
            return self.values[key]
        elif self.orientation == "Column":
            return self.values[0][key]

    def __setitem__(self, key, value):
        pass

    def __len__(self):
        if self.orientation == "Row":
            return len(self.values)
        elif self.orientation == "Column":
            return len(self.values[0])
        
    def __str__(self):
        string = ""
        if self.orientation == "Row":
            for value in self.values:
                string += str(value) + "\\n"
        elif self.orientation == "Column":
            for value in self.values[0]:
                string += str(value) + "\\n"
        return string
        
"""

class Program:
    def __init__(self, name):
        self.methods = []
        self.name = name
        self.imports = []
    
    def addImport(self, i):
        self.imports.append(i)
    
    def addMethod(self, method):
        if not method in self.methods:
            self.methods.append(method)  
            
    def removeMethod(self, method):
        self.methods.remove(method)      

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
        code = ""
        for i in self.imports:
            code += i + "\n"
        code += "\n\n"
        global dataClass
        code += dataClass
        code += "class " + self.name + ":\n"
        for method in self.methods:
            code += method.compile() + "\n\n"
        code += "program = " + self.name + "()\n"
        code += "program." + mainMethod.name + "()"
        return code

class Code:
    def __init__(self, name):
        self.name = name
        self.inputs = []
        self.outputs = []
        self.setNumInputs(1)
        self.setNumOutputs(1)
        self.code = ""
        self.editted = False
        self.deleted = False
        
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
    
    def compile(self):
        
        argument = "\tdef " + self.name + "(self"
        for arg in self.inputs:
            argument += ", " + arg
        argument += "):\n\t\t"
        
        output = "return ("
        first = True
        for out in self.outputs:
            if first:
                first = False
            else:
                output += ", "
            output += out
        output += ")"
        
        return argument + self.code.replace("\n", "\n\t\t") + output
                
class Method:
    def __init__(self, name):
        self.name = name
        self.inputs = []
        self.nodes = []
        self.outputs = []
        self.setNumInputs(1)
        self.setNumOutputs(1)
        self.editted = False
        self.deleted = False
        
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
    
    def updatePriority(self, code, node, priority):
        
        for node in self.nodes:
            node.releaseUpdateLock()
        
        processList = Queue.Queue()
        processList.put_nowait((node, priority))
        
        while not processList.empty():
            (node, priority) = processList.get_nowait()
            
            node.priority = priority
            
            for i in range(len(code)):
                entry = code[i]
                if entry[2] == node:
                    code[i] = (priority, entry[1], entry[2])
                    break
            
            for key in node.links.keys():
                tuple = node.links[key]
                if len(tuple) == 0:
                    continue
                linked = tuple[0]

                if (not linked.updating) and priority+1 > linked.priority:
                    processList.put_nowait((linked, priority+1))
                    linked.updating = True
    
    def compile(self):
        for node in self.nodes:
            node.reset()
        
        processList = Queue.Queue() 
        data = {}
        data["Queue"] = processList
        data["NameMap"] = {}
        data["NameMap"]["Used"] = copy.deepcopy(self.inputs)
        data["NameMap"]["Arguments"] = copy.deepcopy(self.inputs)
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
                    if linked.processed:
                        self.updatePriority(data["Code"], linked, node.priority+1)
                    else:
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
        self.processed = False
        self.priority = 0
        
    def releaseUpdateLock(self):
        self.updating = False
    
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
    
    def writeCode(self, data, code):
        data["Code"].append((self.priority, code, self))
        self.processed = True
    
    def getMappedName(self, node, name, nameMap):
        if node in nameMap and name in nameMap[node]:
            return nameMap[node][name]
        elif name in nameMap["Arguments"]:
            return name
        else:
            usedNames = nameMap["Used"]
                
            bn = "value"
            i = 0
            nn = bn + str(i)
            while nn in usedNames:
                i+=1
                nn = bn + str(i)
            
            usedNames.append(nn)
            
            if not node in nameMap:
                nameMap[node] = {}
            nameMap[node][name] = nn
            return nn

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
        code = self.getMappedName(self, self.links.keys()[0], data["NameMap"])  + " = Data(" + self.name + ")"
        self.writeCode(data, code)
    
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
                
            data["Return"][key] = self.getMappedName(node, nodename, data["NameMap"])
            
        self.processed = True

class PrintNode(TerminalNode):
    def __init__(self):
        Node.__init__(self, "Print")
        self.links = {}
        self.links["Print"] = ()
        
    def process(self, data):
        code = "print " + self.getMappedName(self.links["Print"][0], self.links["Print"][1], data["NameMap"])
        self.writeCode(data, code)
        
class FileWriteNode(TerminalNode):
    def __init__(self):
        Node.__init__(self, "File Write")
        
        self.links = {}
        self.links["Filename"] = ()
        self.links["Contents"] = ()
        
    def process(self, data):
        code = "file = open(" + self.getMappedName(self.links["Filename"][0], self.links["Filename"][1], data["NameMap"]) + "[0], 'w')\n\t\t"
        code += "file.write(" + self.getMappedName(self.links["Contents"][0], self.links["Contents"][1], data["NameMap"]) + ")\n\t\t"
        code += "file.close()"
        self.writeCode(data, code)

class FileReadNode(Node):
    def __init__(self):
        Node.__init__(self, "File Read")
        self.outputs = []
        
        self.links = {}
        self.links["Filename"] = ()
        self.outputs.append("Contents")
    
    def process(self, data):
        code = "file = open(" + self.getMappedName(self.links["Filename"][0], self.links["Filename"][1], data["NameMap"]) + "[0], 'rb')\n\t\t"
        code += self.getMappedName(self, self.outputs[0], data["NameMap"]) + " = file.read()\n\t\t"
        code += "file.close()"
        self.writeCode(data, code)

class ArithmeticNode(Node):
    def __init__(self):
        Node.__init__(self, "Add")
        self.outputs = []
        
        self.setNumInputs(2)
        self.outputs.append("Result")
        
    def setOperator(self, operation):
        self.name = operation
        
    def setNumInputs(self, num):
        prevlinks = self.links
        self.links = {}
        for i in range(num):
            key = "Input"+str(i)
            self.links[key] = ()
            if key in prevlinks:
                self.links[key] = prevlinks[key]
    
    def process(self, data):
        code = self.getMappedName(self, self.outputs[0], data["NameMap"]) + " = Data(["
        num = len(self.links)
        
        operator = "+"
        if self.name == "Subtract":
            operator = "-"
        elif self.name == "Multiply":
            operator = "*"
        elif self.name == "Divide":
            operator = "/"
            
        for i in range(num-2):
            code += "("
        for i in range(num):
            link = self.links["Input"+str(i)]
            if i > 0:
                code += " " + operator + " "
            code += self.getMappedName(link[0], link[1], data["NameMap"]) + "[i]"
            if num > 1 and i > 0 and i < num-1:
                code += ")"
        code += " for i in range(max("
        for i in range(num):
            link = self.links["Input"+str(i)]
            if i > 0:
                code += ", "
            code += "len(" + self.getMappedName(link[0], link[1], data["NameMap"]) + ")"
        code += "))])"
        
        self.writeCode(data, code)
 
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
            string += self.getMappedName(self, key, data["NameMap"])
            
        string += ") = self." + self.method.name + "("
        
        first = True
        for key in self.links.keys() :
            (node, nodename) = self.links[key]
            if not first :
                string += ", "
            else :
                first = False
            string += self.getMappedName(node, nodename, data["NameMap"])
        
        string += ")"
        
        self.writeCode(data, string)

class ConditionalSelectorNode(Node):
    def __init__(self):
        Node.__init__(self, "Equals")
        self.links = {}
        self.links["TestValue1"] = ()
        self.links["TestValue2"] = ()
        self.links["SuccessValue"] = ()
        self.links["FailureValue"] = ()
        self.outputs = ["Selected"]
        
    def setOperator(self, operator):
        self.name = operator
    
    def nameToOperator(self):
        if self.name == "Equals":
            return "=="
        elif self.name == "Greater Than":
            return ">"
        elif self.name == "Equal Or Greater Than":
            return ">="
        elif self.name == "Less Than":
            return "<"
        elif self.name == "Equal Or Less Than":
            return "<="
      
    def process(self, data):
        
        code = self.getMappedName(self, self.outputs[0], data["NameMap"]) + " = Data(["
        
        code += self.getMappedName(self.links["SuccessValue"][0], self.links["SuccessValue"][1], data["NameMap"]) + "[i]"
        code += " if ("
        code += self.getMappedName(self.links["TestValue1"][0], self.links["TestValue1"][1], data["NameMap"]) + "[i]"
        code += " " + self.nameToOperator() + " "
        code += self.getMappedName(self.links["TestValue2"][0], self.links["TestValue2"][1], data["NameMap"]) + "[i]"
        code += ") else "
        code += self.getMappedName(self.links["FailureValue"][0], self.links["FailureValue"][1], data["NameMap"]) + "[i]"
        code += " for i in range(max("
        code += "len(" + self.getMappedName(self.links["TestValue1"][0], self.links["TestValue1"][1], data["NameMap"]) + "), "
        code += "len(" + self.getMappedName(self.links["TestValue2"][0], self.links["TestValue2"][1], data["NameMap"]) + ")"
        
        code += "))])"
                
        self.writeCode(data, code)
        
class CSVParserNode(Node):
    def __init__(self):
        Node.__init__(self, "CSV Parser")
        self.outputs = ["CSV Data"]
        
        self.links = {}
        self.links["CSV"] = ()
        
        self.delimiter = ","
        self.quotechar = '"'
        self.datatype = "float"
    
    def process(self, data):
        code = "reader = csv.reader(" + self.getMappedName(self.links["CSV"][0], self.links["CSV"][1], data["NameMap"]) + "[0].splitlines(), delimiter='" + self.delimiter + "', quotechar='" + self.quotechar + "')\n\t\t"
        code += self.getMappedName(self, self.outputs[0], data["NameMap"]) + " = Data([["+self.datatype+"(element) for element in row] for row in reader])"
        self.writeCode(data, code)

class DataSettingsNode(Node):
    def __init__(self):
        Node.__init__(self, "Data Settings")
        self.outputs = ["Data Out"]
        
        self.links = {}
        self.links["Data In"] = ()
        
        self.orientation = "Row"
        self.iteration = "Single"
        
    def process(self, data):
        code = self.getMappedName(self, self.outputs[0], data["NameMap"]) + " = Data(" + self.getMappedName(self.links["Data In"][0], self.links["Data In"][1], data["NameMap"]) + ".values, iteration='"+self.iteration+"', orientation='"+self.orientation+"')"
        self.writeCode(data, code)

class CodeNode(MethodNode):
    pass

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
    







