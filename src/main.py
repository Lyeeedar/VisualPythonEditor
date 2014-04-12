
from Tkinter import *
import ttk
from Language import *

class GUIInput(Label):
    def __init__(self, parent, name):
        Label.__init__(self, parent, background="blue", text=name, relief="sunken", bd=1)
        self.parent = parent
        self.name = name
        self.pack(fill=BOTH, expand=1)
        
        self.bind("<Enter>", self.mouseIn)
        self.bind("<Leave>", self.mouseOut)
        self.bind("<Button-1>", self.mouseDown)
        
    def mouseIn(self, event):
        self.config(relief="raised")
        
    def mouseOut(self, event):
        self.config(relief="sunken")
        
    def mouseDown(self, event):
        self.parent.parent.startInputLink(self.parent, self.name)
        
class GUIOutput(Label):
    def __init__(self, parent, name):
        Label.__init__(self, parent, background="green", text=name, relief="sunken", bd=1)
        self.grid(sticky=E)
        self.parent = parent
        self.name = name
        self.pack(fill=BOTH, expand=1)
        
        self.bind("<Enter>", self.mouseIn)
        self.bind("<Leave>", self.mouseOut)
        self.bind("<Button-1>", self.mouseDown)
        
    def mouseIn(self, event):
        self.config(relief="raised")
        
    def mouseOut(self, event):
        self.config(relief="sunken")
        
    def mouseDown(self, event):
        self.parent.parent.startOutputLink(self.parent, self.name)
        
class GUINode(Frame):
    def __init__(self, parent, node):
        Frame.__init__(self, parent, background="white", relief="raised", borderwidth=2)
        
        self.node = node
        self.parent = parent
        self.inputNodes = {}
        self.outputNodes = {}
        
        Grid.columnconfigure(self, 0, weight=1)
        Grid.columnconfigure(self, 1, weight=1)
        self.title = Label(self, text=node.name)
        self.title.grid(row=0, columnspan=2, sticky=N+S+E+W)
        
        self.title.bind("<Button-1>", self.mouseDown)
        self.title.bind("<B1-Motion>", self.mouseDrag)
        
        self.setPos(0, 0)
        self.updateLinks()
                
        
    def setPos(self, x, y):
        self.x = x
        self.y = y
        self.place(x=self.x, y=self.y)
        
        self.parent.updateLinks()
        
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
        
        x = self.x+node.winfo_x()
        y = self.y+node.winfo_y()
        
        return (x, y)
    
    def updateLinks(self):
        for key in self.node.links.keys():
            link = self.node.links[key]
            if len(link) > 0:
                onode = link[0]
                guionode = self.parent.nodeMap[onode]
                onodekey = link[1]
                self.parent.addLink(guionode, onodekey, self, key)

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
            if var[0] == 1 and not var[1] in self.node.node.links:
                self.node.node.links[var[1]] = ()
            elif var[0] == 0 and var[1] in self.node.node.links:
                del self.node.node.links[var[1]]
        self.node.create()
        self.destroy()
                    
    def cancel(self):
        self.destroy()

class GUIArgumentNode(GUINode):
    def __init__(self, parent, node):
        GUINode.__init__(self, parent, node)
            
        self.title.bind("<Button-3>", self.mouseRight)
        
        # create a popup menu
        self.aMenu = Menu(self, tearoff=0)
        self.aMenu.add_command(label="Edit", command=self.edit)
        
        self.frame = Frame(self)
        self.pack(fill=BOTH, expand=1)
        self.create()
        
    def create(self):
        
        self.frame.destroy()
        self.frame = Frame(self)
        
        self.outputNodes = {}
        i = 1
        for key in self.node.links.keys():
            Label(self.frame, text="     ").grid(row=i, column=0, sticky=N+S+E+W)
            link = GUIOutput(self.frame, key)
            self.outputNodes[key] = link
            link.grid(row=i, column=1, sticky=N+S+E+W, pady=2)
            i += 1
            
        self.frame.pack(fill=BOTH, expand=1)
        
        
    def mouseRight(self, event):
        self.aMenu.post(event.x_root, event.y_root)
    
    def edit(self):
        GUIArgumentEditFrame(self, self.parent.method, self)
        
class GUIOutputNode(GUINode):
    def __init__(self, parent, node):
        GUINode.__init__(self, parent, node)
        
        i = 1
        for key in node.links.keys():
            link = GUIInput(self, key)
            self.inputNodes[key] = link
            link.grid(row=i, column=0, sticky=N+S+E+W, pady=2)
            Label(self, text="     ").grid(row=i, column=1, sticky=N+S+E+W)
            i += 1
    
class GUIMethodNode(GUINode):
    def __init__(self, parent, node):
        GUINode.__init__(self, parent, node)
        
        i = 1
        for key in node.links.keys():
            link = GUIInput(self, key)
            self.inputNodes[key] = link
            link.grid(row=i, column=0, sticky=N+S+E+W, pady=2)
            i += 1
            
        i = 1
        for key in node.outputs:
            link = GUIOutput(self, key)
            self.outputNodes[key] = link
            link.grid(row=i, column=1, sticky=N+S+E+W, pady=2)
            i += 1

class GUIMethod(Frame):
    def __init__(self, parent, method):
        Frame.__init__(self, parent, background="white")   
        self.parent = parent
        
        self.method = method
        self.linking = False
        self.link = [None, None]
        
        self.canvas = Canvas(self, bg="white")
        self.canvas.pack(fill=BOTH, expand=1)
        
        self.nodes = []
        self.nodeMap = {}
        self.links = []
        for node in method.nodes:
            snode = None
            if isinstance(node, ArgumentNode):
                snode = GUIArgumentNode(self, node)
            elif isinstance(node, OutputNode):
                snode = GUIOutputNode(self, node)
            elif isinstance(node, MethodNode):
                snode = GUIMethodNode(self, node)
            
            self.canvas.create_window(snode.x, snode.y, anchor=NW, window=snode)
            self.nodes.append(snode)
            self.nodeMap[node] = snode
        
        self.pack(fill=BOTH, expand=1)
        
        self.canvas.bind("<Button-3>", self.mouseRight)
        
        # create a popup menu
        self.aMenu = Menu(self, tearoff=0)
        self.aMenu.add_command(label="New Method Node", command=self.addMethodNode)
        self.aMenu.add_command(label="New Input Node", command=self.addInputNode)
        self.aMenu.add_command(label="New Output Node", command=self.addOutputNode)
        self.aMenu.add_command(label="Edit Method", command=self.showMethodEdit)
    def addLink(self, sn, skey, en, ekey):
        for i in range(len(self.links)):
            link = self.links[i]
            if en == link[1][0] and ekey == link[1][1]:
                del self.links[i]
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
        
    def mouseRight(self, event):
        self.aMenu.post(event.x_root, event.y_root)

    def addMethodNode(self):
        node = MethodNode(createEmptyMethod())
        method.addNode(node)
        
        snode = GUIMethodNode(self, node)
        self.canvas.create_window(snode.x, snode.y, anchor=NW, window=snode)
        self.nodes.append(snode)
        self.nodeMap[node] = snode
                
        self.pack(fill=BOTH, expand=1)
        
    def addInputNode(self):
        node = ArgumentNode()
        node.set([self.method.inputs[0]])
        method.addNode(node)
        
        snode = GUIArgumentNode(self, node)
        self.canvas.create_window(snode.x, snode.y, anchor=NW, window=snode)
        self.nodes.append(snode)
        self.nodeMap[node] = snode
                
        self.pack(fill=BOTH, expand=1)
        
    def addOutputNode(self):
        node = OutputNode()
        node.set([self.method.outputs[0]])
        method.addNode(node)
        
        snode = GUIOutputNode(self, node)
        self.canvas.create_window(snode.x, snode.y, anchor=NW, window=snode)
        self.nodes.append(snode)
        self.nodeMap[node] = snode
                
        self.pack(fill=BOTH, expand=1)
        
    def updateLinks(self):
        self.canvas.delete("Link")
        for link in self.links:
            (ox, oy) = link[0][0].getLinkPos(link[0][1], "Output")
            (ix, iy) = link[1][0].getLinkPos(link[1][1], "Input")          
            self.canvas.create_line(ox, oy, ix, iy, tag="Link")
            
    def comparison(self, node, link):
        return link[0][0] == node or link[1][0] == node
    def deleteLinks(self, node):
        self.links[:] = [link for link in self.links if self.comparison(node, link)]
        self.updateLinks()
        # need to remove link from nodes
        
    def showMethodEdit(self):
        MethodEditWindow(self, self.method)  
        
def createEmptyMethod():
    method = Method("Empty Method")
    
    argNode = ArgumentNode()
    argNode.set(method.inputs)
    
    outNode = OutputNode()
    outNode.set(method.outputs)
    
    outNode.addLink(outNode.links.keys()[0], argNode, argNode.links.keys()[0])
        
    method.addNode(argNode)
    method.addNode(outNode)
        
    return method

class MethodEditWindow(Toplevel):
    def __init__(self, parent, method):
        Toplevel.__init__(self, parent, background="white")   
         
        self.parent = parent
        self.method = method
        
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
        self.methodname.insert(0, method.name)
        Label(self.frame, text="Inputs:").grid(row=2, column=0, columnspan=2, sticky=N+S+E+W)
        Label(self.frame, text="Outputs:").grid(row=2, column=2, columnspan=2, sticky=N+S+E+W)
        
        self.methodinputs = []
        i=3
        for input in method.inputs:
            mi = Entry(self.frame)
            mi.grid(row=i, column=0, columnspan=1, sticky=N+S+E+W)
            self.methodinputs.append(mi)
            mi.insert(0, input)
            
            b = Button(self.frame, text="Remove", command=lambda: self.removeInput(input))
            b.grid(row=i, column=1, columnspan=1, sticky=N+S+E+W)
            
            i+=1
            
        b = Button(self.frame, text="Add", command=lambda: self.addInput("Input0"))
        b.grid(row=i, column=0, columnspan=2, sticky=N+S+E+W)
        
        self.methodoutputs = []
        i=3
        for output in method.outputs:
            mi = Entry(self.frame)
            mi.grid(row=i, column=2, columnspan=1, sticky=N+S+E+W)
            self.methodoutputs.append(mi)
            mi.insert(0, output)
            
            b = Button(self.frame, text="Remove", command=lambda: self.removeOutput(output))
            b.grid(row=i, column=3, columnspan=1, sticky=N+S+E+W)
            
            i+=1
        
        b = Button(self.frame, text="Add", command=lambda: self.addOutput("Output0"))
        b.grid(row=i, column=2, columnspan=2, sticky=N+S+E+W)
        
        self.frame.pack(fill=BOTH, expand=1)
        self.pack(fill=BOTH, expand=1)
    
    def addInput(self, name):
        self.method.inputs.append(name)
        self.create()
        
    def addOutput(self, name):
        self.method.outputs.append(name)
        self.create()
    
    def removeInput(self, input):
        print "delete "+input
        for i in self.method.inputs:
            print i
        self.method.inputs.remove(input)
        self.create()
        
    def removeOutput(self, output):
        print "delete "+output
        for i in self.method.outputs:
            print i
        self.method.outputs.remove(output)
        self.create()
        

class MainWindow(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent, background="white")   
         
        self.parent = parent
        
        Grid.columnconfigure(self, 0, weight=1)
        Grid.columnconfigure(self, 1, weight=2)
        
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=0, column=1, sticky=N+S+E+W, pady=5)
        self.notebook.pack(fill=BOTH, expand=1)
        
        method = createEmptyMethod()
        
        guimethod = GUIMethod(self.notebook, method)
        self.notebook.add(guimethod, text=method.name)
        
        self.pack(fill=BOTH, expand=1)

def main():
  
    root = Tk()
    root.geometry("600x400+300+300")
    root.title("Visual Python Editor")
    app = MainWindow(root)
    root.mainloop()  


main()