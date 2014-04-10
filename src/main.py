
from Tkinter import Tk, Frame, BOTH, Button, Label, Grid, N, S, E, W
from Language import *

class GUIInput(Label):
    def __init__(self, parent, name):
        Label.__init__(self, parent, background="blue", text=name)
        self.parent = parent
        self.name = name
        self.pack(fill=BOTH, expand=1)
        
class GUIOutput(Label):
    def __init__(self, parent, name):
        Label.__init__(self, parent, background="green", text=name)
        self.grid(sticky=E)
        self.parent = parent
        self.name = name
        self.pack(fill=BOTH, expand=1)
        
class GUINode(Frame):
    def __init__(self, parent, node):
        Frame.__init__(self, parent, background="white", relief="raised", borderwidth=2)
        
        self.node = node
        self.parent = parent
        
        Grid.columnconfigure(self, 0, weight=1)
        Grid.columnconfigure(self, 1, weight=1)
        self.title = Label(self, text=node.name)
        self.title.grid(row=0, columnspan=2, sticky=N+S+E+W)
        
        self.title.bind("<Button-1>", self.mouseDown)
        self.title.bind("<B1-Motion>", self.mouseDrag)
        
        self.x = 0
        self.y = 0
        self.place(x=self.x, y=self.y)
        
    def mouseDown(self, event):
        self.lx = event.x_root
        self.ly = event.y_root
        
    def mouseDrag(self, event):
        self.x += event.x_root - self.lx
        self.y += event.y_root - self.ly
        
        self.lx = event.x_root
        self.ly = event.y_root
        
        self.place(x=self.x, y=self.y)

class GUIArgumentNode(GUINode):
    def __init__(self, parent, node):
        GUINode.__init__(self, parent, node)
        
        self.outputs = []
        i = 1
        for key in node.links.keys():
            Label(self, text="     ").grid(row=i, column=0, sticky=N+S+E+W)
            self.outputs.append(GUIOutput(self, key).grid(row=i, column=1, sticky=N+S+E+W, pady=2))
            i += 1
            
        self.pack()
        
class GUIOutputNode(GUINode):
    def __init__(self, parent, node):
        GUINode.__init__(self, parent, node)
        
        self.inputs = []
        i = 1
        for key in node.links.keys():
            self.inputs.append(GUIInput(self, key).grid(row=i, column=0, sticky=N+S+E+W, pady=2))
            Label(self, text="     ").grid(row=i, column=1, sticky=N+S+E+W)
            i += 1
            
        self.pack()
    
class GUIMethodNode(GUINode):
    def __init__(self, parent, node):
        GUINode.__init__(self, parent, node)
        
        self.inputs = []
        i = 1
        for key in node.links.keys():
            self.inputs.append(GUIInput(self, key).grid(row=i, column=0, sticky=N+S+E+W, pady=2))
            i += 1
            
        self.outputs = []
        i = 1
        for key in node.outputs:
            self.outputs.append(GUIOutput(self, key).grid(row=i, column=1, sticky=N+S+E+W, pady=2))
            i += 1
        
        self.pack()

class GUIMethod(Frame):
    def __init__(self, parent, method):
        Frame.__init__(self, parent, background="white")   
        self.parent = parent
        
        self.nodes = []
        for node in method.nodes:
            if isinstance(node, ArgumentNode):
                self.nodes.append(GUIArgumentNode(self, node))
            elif isinstance(node, OutputNode):
                self.nodes.append(GUIOutputNode(self, node))
            elif isinstance(node, MethodNode):
                self.nodes.append(GUIMethodNode(self, node))
        
        self.pack(fill=BOTH, expand=1)
        
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

class Example(Frame):
  
    def __init__(self, parent):
        Frame.__init__(self, parent, background="white")   
         
        self.parent = parent
        
        self.initUI()
    
    def initUI(self):
      
        self.parent.title("Simple")
        self.pack(fill=BOTH, expand=1)
        
        quitButton = Button(self, text="Quit",
            command=self.quit)
        quitButton.place(x=150, y=50)
        
        
        method = createEmptyMethod()
        
        GUIMethod(self, method)
        #GUIArgumentNode(self, argNode)

def main():
  
    root = Tk()
    root.geometry("250x150+300+300")
    app = Example(root)
    root.mainloop()  


if __name__ == '__main__':
    main()  