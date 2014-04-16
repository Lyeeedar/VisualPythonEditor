
from Tkinter import *
from Language import *
import ttk
import subprocess

class GUIInput:
    def __init__(self, parent, name):
        self.parent = parent
        self.name = name
        self.label = None
        
    def create(self, guiparent=None):
        if self.label != None:
            self.label.destroy()
        if guiparent == None:
            guiparent = self.guiparent
        self.guiparent = guiparent
        self.label = Label(guiparent, background="blue", text=self.name, relief="sunken", bd=1)
        
        self.label.pack(fill=BOTH, expand=1)
        
        self.label.bind("<Enter>", self.mouseIn)
        self.label.bind("<Leave>", self.mouseOut)
        self.label.bind("<Button-1>", self.mouseDown)
        
    def destroy(self):
        self.label.destroy()
        
    def mouseIn(self, event):
        self.label.config(relief="raised")
        
    def mouseOut(self, event):
        self.label.config(relief="sunken")
        
    def mouseDown(self, event):
        self.parent.parent.startInputLink(self.parent, self.name)
        
class GUIOutput:
    def __init__(self, parent, name):
        self.parent = parent
        self.name = name
        self.label = None
        
    def create(self, guiparent=None):
        if self.label != None:
            self.label.destroy()
        if guiparent == None:
            guiparent = self.guiparent
        self.guiparent = guiparent
        self.label = Label(guiparent, background="green", text=self.name, relief="sunken", bd=1)
        
        self.label.pack(fill=BOTH, expand=1)
        
        self.label.bind("<Enter>", self.mouseIn)
        self.label.bind("<Leave>", self.mouseOut)
        self.label.bind("<Button-1>", self.mouseDown)
        
    def destroy(self):
        self.label.destroy()
        
    def mouseIn(self, event):
        self.label.config(relief="raised")
        
    def mouseOut(self, event):
        self.label.config(relief="sunken")
        
    def mouseDown(self, event):
        self.parent.parent.startOutputLink(self.parent, self.name)
        
class GUINode:
    def __init__(self, parent, node):
        self.node = node
        self.parent = parent
        self.inputNodes = {}
        self.outputNodes = {}
        self.frame = None
        self.canEdit = True
        self.x = 0
        self.y = 0
        
    def create(self, guiparent=None):
        if self.frame != None:
            self.frame.destroy()
        if guiparent == None:
            guiparent = self.guiparent
        self.guiparent = guiparent
        self.frame = Frame(guiparent, background="white", relief="raised", borderwidth=2)
        self.frame.grid(row=0, sticky=N+S+E+W)
        
        Grid.columnconfigure(self.frame, 0, weight=1)
        self.title = Label(self.frame, text=self.node.name)
        self.title.grid(row=0, sticky=N+S+E+W)   
        
        self.title.bind("<Button-1>", self.mouseDown)
        self.title.bind("<B1-Motion>", self.mouseDrag)
        
        self.linkframe = Frame(self.frame, background="white", relief="raised", borderwidth=2)
        self.linkframe.grid(row=1, sticky=N+S+E+W)
        Grid.columnconfigure(self.linkframe, 0, weight=1)
        Grid.columnconfigure(self.linkframe, 1, weight=1)
        
        self.updateLinks()
        
        self.frame.place(x=self.x, y=self.y)
        
        self.createMenu()
        
    def createMenu(self):
        self.title.bind("<Button-3>", self.mouseRight)
        
        # create a popup menu
        self.aMenu = Menu(self.frame, tearoff=0)
        if self.canEdit:
            self.aMenu.add_command(label="Edit", command=self.edit)
        self.aMenu.add_command(label="Delete", command=self.delete)
                  
    def setPos(self, x, y):
        self.x = x
        self.y = y
        self.frame.place(x=self.x, y=self.y)
        
        self.parent.updateLinks()
        
    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        self.setPos(self.x, self.y)
        
    def mouseDown(self, event):
        self.lx = event.x_root
        self.ly = event.y_root
        
    def mouseDrag(self, event):
        self.x += event.x_root - self.lx
        self.y += event.y_root - self.ly
        
        self.lx = event.x_root
        self.ly = event.y_root
        
        self.setPos(self.x, self.y)
        
    def getLinkPos(self, key, inout):
        node = None
        if inout == "Output":
            node = self.outputNodes[key]
        else:
            node = self.inputNodes[key]
        
        x = self.x+self.linkframe.winfo_x()+node.label.winfo_x()
        y = self.y+self.linkframe.winfo_y()+node.label.winfo_y()
        
        return (x, y)
    
    def updateLinks(self):
        for key in self.node.links.keys():
            link = self.node.links[key]
            if len(link) > 0:
                onode = link[0]
                guionode = self.parent.nodeMap[onode]
                onodekey = link[1]
                self.parent.addLink(guionode, onodekey, self, key)
                
    def edit(self):
        pass

    def delete(self):
        self.frame.destroy()
        self.parent.removeNode(self)

class GUIArgumentEditFrame(Toplevel):
    def __init__(self, parent, method, node):
        Toplevel.__init__(self, parent, background="white")
        self.geometry("360x240+300+300") 
         
        self.parent = parent
        self.method = method
        self.node = node
        
        self.frame = Frame(self)
        self.create()
        self.frame.pack(fill=BOTH, expand=1)
        
    def create(self):
        Grid.columnconfigure(self.frame, 0, weight=1)
        Grid.columnconfigure(self.frame, 1, weight=1)
        
        Label(self.frame, text="Method Input Node").grid(row=0, column=0, columnspan=2, sticky=N+S+E+W)
        
        self.inputs = []
        i = 1
        for input in self.method.inputs:
            var = IntVar()
            c = Checkbutton(self.frame, text=input, variable=var)
            if input in self.node.node.links:
                c.select()
            c.grid(row=i, column=0, columnspan=2, sticky=N+S+E+W)
            self.inputs.append((var, input))
            i+=1
        Button(self.frame, text="Apply", command=self.apply).grid(row=i, column=0, columnspan=1, sticky=N+S+E+W)
        Button(self.frame, text="Cancel", command=self.cancel).grid(row=i, column=1, columnspan=1, sticky=N+S+E+W)
        
    def apply(self):
        for var in self.inputs:
            if var[0].get() == 1 and not var[1] in self.node.node.links:
                self.node.node.links[var[1]] = ()
            elif var[0].get() == 0 and var[1] in self.node.node.links:
                self.node.parent.deleteLinks(self.node, var[1])
                del self.node.node.links[var[1]]
        self.node.create()
        self.destroy()
                    
    def cancel(self):
        self.destroy()

class GUIArgumentNode(GUINode):
    def __init__(self, parent, node):
        GUINode.__init__(self, parent, node)
        
    def create(self, guiparent=None):
        if guiparent == None:
            guiparent = self.guiparent
        self.guiparent = guiparent
        GUINode.create(self, guiparent)
        
        self.createMenu()
             
        i = 1
        for key in self.node.links.keys():
            Label(self.linkframe, text="     ").grid(row=i, column=0, sticky=N+S+E+W)
            link = GUIOutput(self, key)
            link.create(self.linkframe)
            self.outputNodes[key] = link
            link.label.grid(row=i, column=1, sticky=N+S+E+W, pady=2)
            i += 1        
      
    def mouseRight(self, event):
        self.aMenu.post(event.x_root, event.y_root)
    
    def edit(self):
        GUIArgumentEditFrame(self.frame, self.parent.method, self)
        
    def verify(self):
        for key in self.node.links.keys():
            if not key in self.parent.method.inputs:
                self.parent.deleteLinks(self, key)
                del self.node.links[key]
        
class GUIOutputEditFrame(Toplevel):
    def __init__(self, parent, method, node):
        Toplevel.__init__(self, parent, background="white")
        self.geometry("360x240+300+300") 
         
        self.parent = parent
        self.method = method
        self.node = node
        
        self.frame = Frame(self)
        self.create()
        self.frame.pack(fill=BOTH, expand=1)
        
    def create(self):
        Grid.columnconfigure(self.frame, 0, weight=1)
        Grid.columnconfigure(self.frame, 1, weight=1)
        
        Label(self.frame, text="Method Output Node").grid(row=0, column=0, columnspan=2, sticky=N+S+E+W)
        
        self.outputs = []
        i = 1
        for output in self.method.outputs:
            var = IntVar()
            c = Checkbutton(self.frame, text=output, variable=var)
            if output in self.node.node.links:
                c.select()
            c.grid(row=i, column=0, columnspan=2, sticky=N+S+E+W)
            self.outputs.append((var, output))
            i+=1
        Button(self.frame, text="Apply", command=self.apply).grid(row=i, column=0, columnspan=1, sticky=N+S+E+W)
        Button(self.frame, text="Cancel", command=self.cancel).grid(row=i, column=1, columnspan=1, sticky=N+S+E+W)
        
    def apply(self):
        for var in self.outputs:
            if var[0].get() == 1 and not var[1] in self.node.node.links:
                self.node.node.links[var[1]] = ()
            elif var[0].get() == 0 and var[1] in self.node.node.links:
                self.node.parent.deleteLinks(self.node, var[1])
                del self.node.node.links[var[1]]
        self.node.create()
        self.destroy()
                    
    def cancel(self):
        self.destroy()

class GUIOutputNode(GUINode):
    def __init__(self, parent, node):
        GUINode.__init__(self, parent, node)
        
    def create(self, guiparent=None):
        if guiparent == None:
            guiparent = self.guiparent
        self.guiparent = guiparent
        GUINode.create(self, guiparent)
        
        self.createMenu()
        
        i = 1
        for key in self.node.links.keys():
            link = GUIInput(self, key)
            link.create(self.linkframe)
            self.inputNodes[key] = link
            link.label.grid(row=i, column=0, sticky=N+S+E+W, pady=2)
            Label(self.linkframe, text="     ").grid(row=i, column=1, sticky=N+S+E+W)
            i += 1
     
    def mouseRight(self, event):
        self.aMenu.post(event.x_root, event.y_root)
    
    def edit(self):
        GUIOutputEditFrame(self.frame, self.parent.method, self)
        
    def verify(self):
        for key in self.node.links.keys():
            if not key in self.parent.method.outputs:
                self.parent.deleteLinks(self, key)
                del self.node.links[key]

class GUIValueEditFrame(Toplevel):
    def __init__(self, parent, method, node):
        Toplevel.__init__(self, parent, background="white")
        self.geometry("360x240+300+300") 
         
        self.parent = parent
        self.method = method
        self.node = node
        
        self.frame = Frame(self)
        self.create()
        self.frame.pack(fill=BOTH, expand=1)
        
    def create(self):
        Grid.columnconfigure(self.frame, 0, weight=1)
        Grid.columnconfigure(self.frame, 1, weight=1)
        
        Label(self.frame, text="Value").grid(row=1, column=0, sticky=N+S+E+W)
        self.value = Entry(self.frame)
        self.value.grid(row=1, column=1, sticky=N+S+E+W)
        self.value.insert(0, self.node.node.name)
        
        Button(self.frame, text="Apply", command=self.apply).grid(row=2, column=0, sticky=N+S+E+W)
        Button(self.frame, text="Cancel", command=self.cancel).grid(row=2, column=1, sticky=N+S+E+W)
        
    def apply(self):
        self.node.node.set("Value", self.value.get())
        
        self.node.create()
        self.destroy()
                    
    def cancel(self):
        self.destroy()

class GUIValueNode(GUIArgumentNode):
    def edit(self):
        GUIValueEditFrame(self.frame, self.parent.method, self)
        
    def verify(self):
        pass

class GUIMethodNode(GUINode):
    def __init__(self, parent, node):
        GUINode.__init__(self, parent, node)
        
        self.verify()
        
    def create(self, guiparent=None):
        
        self.node.update()
        
        if guiparent == None:
            guiparent = self.guiparent
        self.guiparent = guiparent
        GUINode.create(self, guiparent)
        
        i = 1
        for key in self.node.links.keys():
            link = GUIInput(self, key)
            link.create(self.linkframe)
            self.inputNodes[key] = link
            link.label.grid(row=i, column=0, sticky=N+S+E+W, pady=2)
            i += 1
            
        i = 1
        for key in self.node.outputs:
            link = GUIOutput(self, key)
            link.create(self.linkframe)
            self.outputNodes[key] = link
            link.label.grid(row=i, column=1, sticky=N+S+E+W, pady=2)
            i += 1
    
    def mouseRight(self, event):
        self.aMenu.post(event.x_root, event.y_root)
    
    def edit(self):
        global app
        app.openMethod(self.node.method, self.parent.program)
        
    def verify(self):
        for key in self.node.links.keys():
            if not key in self.node.method.inputs:
                self.parent.deleteLinks(self, key)
                del self.node.links[key]
        
        for key in self.node.outputs:
            if not key in self.node.method.outputs:
                self.parent.deleteLinks(self, key)
                self.node.outputs.remove(key)
                
class GUIArithmeticEditFrame(Toplevel):
    def __init__(self, parent, method, node):
        Toplevel.__init__(self, parent, background="white")
        self.geometry("360x240+300+300") 
         
        self.parent = parent
        self.method = method
        self.node = node
        
        self.frame = Frame(self)
        self.create()
        self.frame.pack(fill=BOTH, expand=1)
        
    def create(self):
        Grid.columnconfigure(self.frame, 0, weight=1)
        Grid.columnconfigure(self.frame, 1, weight=1)
        
        Label(self.frame, text="Operation").grid(row=0, column=0, columnspan=2, sticky=N+S+E+W)
        
        MODES = ["Add", "Subtract", "Multiply", "Divide"]
        
        self.v = StringVar()
        self.v.set(MODES[0])
        
        i = 1
        for mode in MODES:
            b = Radiobutton(self.frame, text=mode,
                            variable=self.v, value=mode)
            b.grid(row=i, column=0, columnspan=2, sticky=W)
            i+=1
        
        Label(self.frame, text="Num Inputs").grid(row=i, column=0, sticky=N+S+E+W)
                
        OPTIONS = []
        for n in range(18):
            OPTIONS.append(n+2)
                
        self.variable = IntVar(self.frame)
        self.variable.set(len(self.node.node.links)) # default value
        
        w = apply(OptionMenu, (self.frame, self.variable) + tuple(OPTIONS))
        w.grid(row=i, column=1, sticky=N+S+E+W)
        
        i+=1
        
        Button(self.frame, text="Apply", command=self.apply).grid(row=i, column=0, sticky=N+S+E+W)
        Button(self.frame, text="Cancel", command=self.cancel).grid(row=i, column=1, sticky=N+S+E+W)
        
    def apply(self):
        self.node.node.setOperator(self.v.get())
        self.node.node.setNumInputs(self.variable.get())
        
        self.node.create()
        self.destroy()
                    
    def cancel(self):
        self.destroy()

class GUIArithmeticNode(GUIMethodNode):
    def edit(self):
        GUIArithmeticEditFrame(self.frame, self.parent.method, self)
    def verify(self):
        pass
                
class GUIFileReadNode(GUIMethodNode):
    
    def __init__(self, parent, node):
        GUIMethodNode.__init__(self, parent, node)
        self.canEdit = False
    def edit(self):
        pass
    def verify(self):
        pass
    
class GUIFileWriteNode(GUIOutputNode):
    def __init__(self, parent, node):
        GUIOutputNode.__init__(self, parent, node)
        self.canEdit = False
    def edit(self):
        pass
    def verify(self):
        pass

class GUIPrintNode(GUIOutputNode):
    def __init__(self, parent, node):
        GUIOutputNode.__init__(self, parent, node)
        self.canEdit = False
    def edit(self):
        pass
    def verify(self):
        pass

class GUIMethod:
    def __init__(self, parent, method, program):
        self.parent = parent
        
        self.program = program
        self.method = method
        self.linking = False
        self.link = [None, None]
        
        self.nodes = []
        self.nodeMap = {}
        self.links = []
        self.frame = None
        
        for node in method.nodes:
            snode = None
            if isinstance(node, ArgumentNode):
                snode = GUIArgumentNode(self, node)
            elif isinstance(node, OutputNode):
                snode = GUIOutputNode(self, node)
            elif isinstance(node, MethodNode):
                snode = GUIMethodNode(self, node)
            
            self.nodes.append(snode)
            self.nodeMap[node] = snode
                    
    def create(self, guiparent=None):
        if guiparent == None:
            guiparent = self.guiparent
        self.guiparent = guiparent
        if self.frame != None:
            self.frame.destroy()
        self.frame = Frame(guiparent, background="white")   
        
        self.canvas = Canvas(self.frame, bg="white")
        self.canvas.pack(fill=BOTH, expand=1)
        
        self.frame.pack(fill=BOTH, expand=1)
        
        self.canvas.bind("<Button-3>", self.mouseRight)
        self.canvas.bind("<Button-1>", self.mouseDown)
        self.canvas.bind("<B1-Motion>", self.mouseDrag)
        
        # create a popup menu
        self.aMenu = Menu(self.frame, tearoff=0)
        self.aMenu.add_command(label="New Method Node", command=self.addMethodNode)
        self.aMenu.add_command(label="New File Read Node", command=self.addFileReadNode)
        self.aMenu.add_command(label="New Arithmetic Node", command=self.addArithmeticNode)
        self.aMenu.add_command(label="New Input Node", command=self.addInputNode)
        self.aMenu.add_command(label="New Value Node", command=self.addValueNode)
        self.aMenu.add_command(label="New Output Node", command=self.addOutputNode)
        self.aMenu.add_command(label="New Print Node", command=self.addPrintNode)
        self.aMenu.add_command(label="New File Write Node", command=self.addFileWriteNode)
        self.aMenu.add_command(label="Edit Method", command=self.showMethodEdit)
        
        for node in self.nodes:
            node.create(self.canvas)
            self.canvas.create_window(node.x, node.y, anchor=NW, window=node.frame)
            
        self.updateLinks()
            
    def destroy(self):
        self.frame.destroy()
        for node in self.nodes:
            node.destroy()
        
    def addLink(self, sn, skey, en, ekey):
        nlinks = []
        for i in range(len(self.links)):
            link = self.links[i]
            if en == link[1][0] and ekey == link[1][1]:
                pass
            else:
                nlinks.append(link)
        self.links = nlinks
        self.links.append(((sn, skey), (en, ekey)))
    def startInputLink(self, node, name):
        if self.link[1] != None:
            self.cancelLinking()
            return
        self.linking = True
        self.link[1] = (node, name)
        self.validateLinking()
    def startOutputLink(self, node, name):
        if self.link[0] != None:
            self.cancelLinking()
            return
        self.linking = True
        self.link[0] = (node, name)
        self.validateLinking()
    def validateLinking(self):
        if self.link[0] != None and self.link[1] != None:    
            self.link[1][0].node.addLink(self.link[1][1], self.link[0][0].node, self.link[0][1])
            self.addLink(self.link[0][0], self.link[0][1], self.link[1][0], self.link[1][1])
            self.cancelLinking()
            self.updateLinks()
    def cancelLinking(self):
        self.linking = False
        self.link = [None, None]
    
    def mouseDown(self, event):
        self.lx = event.x_root
        self.ly = event.y_root
        
    def mouseDrag(self, event):
        dx = event.x_root - self.lx
        dy = event.y_root - self.ly
        
        self.lx = event.x_root
        self.ly = event.y_root
        
        for node in self.nodes:
            node.move(dx, dy)
    
    def mouseRight(self, event):
        self.aMenu.post(event.x_root, event.y_root)
        self.clickx = event.x
        self.clicky = event.y

    def addMethodNode(self):
        node = MethodNode(createEmptyMethod(self.program))
        self.method.addNode(node)
        
        snode = GUIMethodNode(self, node)
        self.nodes.append(snode)
        self.nodeMap[node] = snode
        
        self.create(self.guiparent)
        snode.setPos(self.clickx, self.clicky)
        
    def addFileReadNode(self):
        node = FileReadNode()
        self.method.addNode(node)
        
        snode = GUIFileReadNode(self, node)
        self.nodes.append(snode)
        self.nodeMap[node] = snode
        
        self.create(self.guiparent)
        snode.setPos(self.clickx, self.clicky)
        
    def addArithmeticNode(self):
        node = ArithmeticNode()
        self.method.addNode(node)
        
        snode = GUIArithmeticNode(self, node)
        self.nodes.append(snode)
        self.nodeMap[node] = snode
        
        self.create(self.guiparent)
        snode.setPos(self.clickx, self.clicky)
                        
    def addInputNode(self):
        node = ArgumentNode()
        node.set([self.method.inputs[0]])
        self.method.addNode(node)
        
        snode = GUIArgumentNode(self, node)
        self.nodes.append(snode)
        self.nodeMap[node] = snode
        
        self.create(self.guiparent)
        snode.setPos(self.clickx, self.clicky)
                        
    def addOutputNode(self):
        node = OutputNode()
        node.set([self.method.outputs[0]])
        self.method.addNode(node)
        
        snode = GUIOutputNode(self, node)
        self.nodes.append(snode)
        self.nodeMap[node] = snode
        
        self.create(self.guiparent)
        snode.setPos(self.clickx, self.clicky)
        
    def addPrintNode(self):
        node = PrintNode()
        self.method.addNode(node)
        
        snode = GUIPrintNode(self, node)
        self.nodes.append(snode)
        self.nodeMap[node] = snode
        
        self.create(self.guiparent)
        snode.setPos(self.clickx, self.clicky)
        
    def addFileWriteNode(self):
        node = FileWriteNode()
        self.method.addNode(node)
        
        snode = GUIFileWriteNode(self, node)
        self.nodes.append(snode)
        self.nodeMap[node] = snode
        
        self.create(self.guiparent)
        snode.setPos(self.clickx, self.clicky)
    
    def addValueNode(self):
        node = ValueNode("Value", "'A String'")
        self.method.addNode(node)
        
        snode = GUIValueNode(self, node)
        self.nodes.append(snode)
        self.nodeMap[node] = snode
        
        self.create(self.guiparent)
        snode.setPos(self.clickx, self.clicky)
    
    def removeNode(self, node):
        
        for key in node.inputNodes.keys():
            self.deleteLinks(node, key)
            
        for key in node.outputNodes.keys():
            self.deleteLinks(node, key)
        
        self.nodes.remove(node)
        del self.nodeMap[node.node]
        self.method.removeNode(node.node)
          
    def updateLinks(self):
        self.canvas.delete("Link")
        for link in self.links:
            (ox, oy) = link[0][0].getLinkPos(link[0][1], "Output")
            (ix, iy) = link[1][0].getLinkPos(link[1][1], "Input")          
            self.canvas.create_line(ox, oy, ix, iy, tag="Link")
            
    def comparison(self, node, key, link):
        if link[0][0] == node and link[0][1] == key:
            return True
        elif link[1][0] == node and link[1][1] == key:
            return True
        return False
    def deleteLinks(self, node, key):
        links = []
        for link in self.links:
            if self.comparison(node, key, link):
                link[1][0].node.removeLink(link[1][1])
            else:
                links.append(link) 
        self.links = links
        self.updateLinks()
        
    def showMethodEdit(self):
        MethodEditWindow(self.frame, self, self.method)
        
    def verify(self):
        for node in self.nodes:
            node.verify()
            node.create()
        
def createEmptyMethod(program):
    method = Method(program.getUnusedName())
    program.addMethod(method)
    
    argNode = ArgumentNode()
    argNode.set(method.inputs)
    
    outNode = OutputNode()
    outNode.set(method.outputs)
    
    outNode.addLink(outNode.links.keys()[0], argNode, argNode.links.keys()[0])
        
    method.addNode(argNode)
    method.addNode(outNode)
        
    return method

class MethodEditWindow(Toplevel):
    def __init__(self, guiparent, parent, method):
        Toplevel.__init__(self, guiparent, background="white")   
         
        self.parent = parent
        self.method = method
        self.inputs = method.inputs
        self.outputs = method.outputs
        self.name = method.name
        
        self.frame = Frame(self)
        self.create()
                
    def create(self):
        
        self.frame.destroy()
        self.frame = Frame(self)
        
        Grid.columnconfigure(self.frame, 0, weight=2)
        Grid.columnconfigure(self.frame, 1, weight=1)
        Grid.columnconfigure(self.frame, 2, weight=2)
        Grid.columnconfigure(self.frame, 3, weight=1)
        
        Label(self.frame, text="Method Name:").grid(row=0, column=0, columnspan=4, sticky=N+S+E+W)
        self.methodname = Entry(self.frame)
        self.methodname.grid(row=1, column=0, columnspan=4, sticky=N+S+E+W)
        self.methodname.insert(0, self.name)
        Label(self.frame, text="Inputs:").grid(row=2, column=0, columnspan=2, sticky=N+S+E+W)
        Label(self.frame, text="Outputs:").grid(row=2, column=2, columnspan=2, sticky=N+S+E+W)
        
        self.methodinputs = []
        i=3
        for input in self.inputs:
            mi = Entry(self.frame)
            mi.grid(row=i, column=0, columnspan=1, sticky=N+S+E+W)
            self.methodinputs.append(mi)
            mi.insert(0, input)
            
            b = Button(self.frame, text="Remove", command=lambda input=input: self.removeInput(input))
            b.grid(row=i, column=1, columnspan=1, sticky=N+S+E+W)
            
            i+=1
            
        b = Button(self.frame, text="Add", command=lambda: self.addInput())
        b.grid(row=i, column=0, columnspan=2, sticky=N+S+E+W)
        
        max = i+1
        
        self.methodoutputs = []
        i=3
        for output in self.outputs:
            mi = Entry(self.frame)
            mi.grid(row=i, column=2, columnspan=1, sticky=N+S+E+W)
            self.methodoutputs.append(mi)
            mi.insert(0, output)
            
            b = Button(self.frame, text="Remove", command=lambda output=output: self.removeOutput(output))
            b.grid(row=i, column=3, columnspan=1, sticky=N+S+E+W)
            
            i+=1
        
        b = Button(self.frame, text="Add", command=lambda: self.addOutput())
        b.grid(row=i, column=2, columnspan=2, sticky=N+S+E+W)
        
        if i+1 > max:
            max = i+1
        
        b = Button(self.frame, text="Apply", command=self.apply)
        b.grid(row=max, column=0, columnspan=2, sticky=N+S+E+W)
        
        b = Button(self.frame, text="Cancel", command=self.cancel)
        b.grid(row=max, column=2, columnspan=2, sticky=N+S+E+W)
        
        self.frame.pack(fill=BOTH, expand=1)
    
    def addInput(self):
        self.read()
        name = "Input0"
        while name in self.inputs:
            name = name+"0"
        self.inputs.append(name)
        self.create()
        
    def addOutput(self):
        self.read()
        name = "Output0"
        while name in self.outputs:
            name = name+"0"
        self.outputs.append(name)
        self.create()
    
    def removeInput(self, input):
        self.read()
        self.inputs.remove(input)
        self.create()
        
    def removeOutput(self, output):
        self.read()
        self.outputs.remove(output)
        self.create()
    
    def gen_valid_identifier(self, seq):
        # get an iterator
        itr = iter(seq)
        # pull characters until we get a legal one for first in identifer
        for ch in itr:
            if ch == '_' or ch.isalpha():
                yield ch
                break
        # pull remaining characters and yield legal ones for identifier
        for ch in itr:
            if ch == '_' or ch.isalpha() or ch.isdigit():
                yield ch
    
    def sanitize_identifier(self, name):
        return ''.join(self.gen_valid_identifier(name))

    def read(self):
        self.inputs = []
        for mi in self.methodinputs:
            self.inputs.append(mi.get())
        self.outputs = []
        for mo in self.methodoutputs:
            self.outputs.append(mo.get())
        self.name = self.methodname.get()
        self.name = self.sanitize_identifier(self.name)
            
    def apply(self):
        self.read()
        
        if not self.parent.program.checkNameUsed(self.name):
            oldname = self.method.name
            self.parent.parent.tabbedpane.changeTabName(oldname, self.name)
            self.method.name = self.name
        
        self.method.inputs = self.inputs
        self.method.outputs = self.outputs
        self.parent.verify()
        self.destroy()
        
    def cancel(self):
        self.destroy()

class TabbedPane(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent, background="white") 
        self.parent = parent
        
        Grid.rowconfigure(self, 0, weight=1)
        Grid.rowconfigure(self, 1, weight=4)
        Grid.columnconfigure(self, 0, weight=1)
        
        self.tabs = []
        self.frame = Frame(self)

        self.buttonframe = Frame(self, height=1)
        self.buttonframe.grid_propagate(0)
        #self.buttonframe.pack(fill=BOTH, expand=1)
        Grid.rowconfigure(self.buttonframe, 0, weight=1)
        self.buttonframe.grid(row=0, sticky=N+S+E+W, padx=5)
        
        self.pack(fill=BOTH, expand=1)

    def addTab(self, name, method):
        found = False
        for tab in self.tabs:
            if name == tab[0]:
                found = True
                break
        
        if not found:
            b = Button(self.buttonframe, text=name, command=lambda name=name: self.setActiveTab(name))
            b.grid(row = 0, column=len(self.tabs), sticky=N+S+E+W, padx=5)
            self.tabs.append([name, method, b])
            
    def setActiveTab(self, name):
        for tab in self.tabs:
            if tab[0] == name:
                self.frame.destroy
                self.frame = Frame(self)
                self.frame.grid(row=1, column=0, sticky=N+S+E+W, pady=5)
                #tab[1].verify()
                tab[1].create(self.frame)
                self.active = tab[1]
                
    def changeTabName(self, name, newname):
        for i in range(len(self.tabs)):
            tab = self.tabs[i]
            if tab[0] == name:
                tab[0] = newname
                tab[2].config(text=newname, command=lambda newname=newname: self.setActiveTab(newname))
                return
        
    def getActive(self):
        return self.active

class MainWindow(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent, background="white")   
         
        self.parent = parent
        
        Grid.rowconfigure(self, 0, weight=1)
        Grid.rowconfigure(self, 1, weight=100)
        
        Grid.columnconfigure(self, 0, weight=1)
        Grid.columnconfigure(self, 1, weight=3)
        Grid.columnconfigure(self, 2, weight=1)
        
        self.addToolbar()
        self.addProgramBrowser()
        self.addTabbedPane()
        self.addConsole()
        
        program = Program("TestProgram")
        method = createEmptyMethod(program)
        
        self.openMethods = {}
        self.openMethod(method, program)
        
        self.pack(fill=BOTH, expand=1)
        
    def addToolbar(self):
        compile = Button(self, text="C", command=self.compile)
        compile.grid(row=0, column=0)
        
        run = Button(self, text="R", command=self.run)
        run.grid(row=0, column=1)
        
    def compile(self):
        method = self.tabbedpane.getActive().method
        program = self.openMethods[method][1]
        code = program.compile(method)
        file = open(program.name+'.py', 'w')
        file.write(code)
        file.close()
        
    def run(self):
        method = self.tabbedpane.getActive().method
        program = self.openMethods[method][1]
        print subprocess.check_output(["python", program.name+".py"])
        
    def addProgramBrowser(self):
        pass
    
    def addTabbedPane(self):
        self.tabbedpane = TabbedPane(self)
        self.tabbedpane.grid(row=1, column=1, sticky=N+S+E+W, pady=5)
        #self.tabbedpane.pack(fill=BOTH, expand=1)
        
    def addConsole(self):
        self.console = Frame(self)
        self.console.grid(row=1, column=2, sticky=N+S+E+W, pady=5)
        
    def openMethod(self, method, program):
        if not method in self.openMethods:
            guimethod = GUIMethod(self, method, program)
            self.tabbedpane.addTab(method.name, guimethod)
            self.openMethods[method] = (guimethod, program)
        self.tabbedpane.setActiveTab(method.name)

app = None
def main():
  
    root = Tk()
    root.geometry("600x400+300+300")
    root.title("Visual Python Editor")
    global app
    app = MainWindow(root)
    root.mainloop()  


main()