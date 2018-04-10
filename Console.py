"""
Console.py provide a tkInter window to use for console messages

Mainly used by print and println in robot scripts

"""
import time
t0=time.clock()
from tkinter import messagebox
from tkinter import *
import tkinter.scrolledtext as tkscrolled
t1=time.clock()
from ConsoleQueue import *
import pygame
from pygame.locals import *
t2=time.clock()
print("Console.py imports tkinter took %.6fs pygame took %.6fs"%(t1-t0,(t2-t1)))

class Console():

    consoleSize=(600,150)

    root=None
    text=None
    menu=None
    scroller=None
    listbox=None

    def __init__(self,**kwargs):

        for k,v in kwargs.items():
            setattr(self,k,v)

        if self.root is None:
            print("CONSOLE root is None using Toplevel()")
            w,h=self.consoleSize
            self.root=Toplevel(width=w,height=h)

        self.root.title("Pixelbot Message Console")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.text=tkscrolled.ScrolledText(master=self.root, wrap="word")
        self.text.config(font=("Arial", 10,))
        self.text.pack(side=RIGHT)

        self.menubar=Menu(self.root,tearoff=0)
        self.mainmenu=Menu(self.menubar,tearoff="0")
        self.mainmenu.add_command(label="Clear Display",command=self.clear)
        self.menubar.add_cascade(label="Main",menu=self.mainmenu)
        self.root.config(menu=self.menubar)

        print("Console setup")


    def on_closing(self):
        messagebox.showinfo("Close Console", "To close the program please close the Script manager window?")

    def clear(self):
        """
        clear text display
        :return:
        """
        r=messagebox.askyesno("Clear Display","do you really want to clear the messages?:")
        if r: self.text.delete(1.0,END)

    def print(self,*args):
        console_print(args)
        self.update()

    def println(self,*args):
        console_println(args)
        self.update()

    def update(self):
        Q=console_getEntries()
        for line in Q:
            self.text.insert(END,line)
        self.text.update()