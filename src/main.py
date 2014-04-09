
from Tkinter import Tk, Frame, BOTH, Button, Label

class GUIMethod(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent, background="white")   
        self.parent = parent
        self.initUI()
        
        self.x = 0
        self.y = 0
        
        self.place(x=self.x, y=self.y)
    
    def initUI(self):
        Label(self, text="MethodName").grid(row=0)
        Label(self, text="Out1").grid(row=1)
        Label(self, text="Out2").grid(row=2)
        
        self.pack()
        
        self.bind("<Button-1>", self.mouseDown)
        self.bind("<B1-Motion>", self.mouseDrag)
        
    def mouseDown(self, event):
        self.lx = event.x_root
        self.ly = event.y_root
        
    def mouseDrag(self, event):
        self.x += event.x_root - self.lx
        self.y += event.y_root - self.ly
        
        self.lx = event.x_root
        self.ly = event.y_root
        
        self.place_configure(x=self.x, y=self.y)
        
        print str(self.x) + "  " + str(self.y)
        

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
        
        GUIMethod(self)

def main():
  
    root = Tk()
    root.geometry("250x150+300+300")
    app = Example(root)
    root.mainloop()  


if __name__ == '__main__':
    main()  