#! /usr/bin/env python
#
# GUI module generated by PAGE version 4.12
# In conjunction with Tcl version 8.6
#    Mar 31, 2018 07:39:48 PM

import sys
import json
from tkinter import *
from tkinter import messagebox

try:
    import ttk
    py3 = False
except ImportError:
    import tkinter.ttk as ttk
    py3 = True


class RobotChooser:

    chosenBotList=[]
    botList={}

    def __init__(self, top=None,robotList="robot.json"):
        # user calls show() to make the dialog visible

        self.top=Toplevel()
        self.top.grab_set() # make this dialog modal

        try:
            f=open(robotList,"r")
            self.botList=json.load(f)
            f.close()

        except Exception as e:
            print("Unable to load",robotList,"Has it been moved?",e.args)
            messagebox.showinfo("Robot Chooser","Unable to open robot data file "+robotList)

    def show(self):
        '''This class configures and populates the toplevel window.
           top is the toplevel containing window.'''
        _bgcolor = '#d9d9d9'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#d9d9d9' # X11 color: 'gray85'
        _ana1color = '#d9d9d9' # X11 color: 'gray85' 
        _ana2color = '#d9d9d9' # X11 color: 'gray85' 

        self.top.geometry("425x286+480+157")
        self.top.title("Robot Chooser")
        self.top.configure(background="#d9d9d9")
        #self.top.configure(highlightbackground="#d9d9d9")
        #self.top.configure(highlightcolor="black")

        self.RobotList = ScrolledListBox(self.top,selectmode=MULTIPLE)
        self.RobotList=Listbox(self.top,selectmode=MULTIPLE)
        self.RobotList.place(relx=0.38, rely=0.07, relheight=0.46, relwidth=0.5)
        self.RobotList.configure(background="white")
        self.RobotList.configure(font="TkFixedFont")
        self.RobotList.configure(foreground="#000000")
        self.RobotList.configure(highlightbackground="#d9d9d9")
        self.RobotList.configure(highlightcolor="black")
        self.RobotList.configure(selectbackground="#c4c4c4")
        self.RobotList.configure(selectforeground="black")
        self.RobotList.configure(selectmode=MULTIPLE)
        self.RobotList.configure(width=214)

        # botList keys are the same as the robot names
        sortedBots=sorted(self.botList.keys(),key=str.lower)
        for bot in sortedBots:
            # botList
            self.RobotList.insert(END,bot)

        self.Label1 = Label(self.top)
        self.Label1.place(relx=0.07, rely=0.07, height=21, width=94)
        self.Label1.configure(activebackground="#f9f9f9")
        self.Label1.configure(activeforeground="black")
        self.Label1.configure(background="#d9d9d9")
        self.Label1.configure(disabledforeground="#a3a3a3")
        self.Label1.configure(foreground="#000000")
        self.Label1.configure(highlightbackground="#d9d9d9")
        self.Label1.configure(highlightcolor="black")
        self.Label1.configure(text='''Robots Available''')

        self.Label2 = Label(self.top)
        self.Label2.place(relx=0.09, rely=0.63, height=21, width=334)
        self.Label2.configure(activebackground="#f9f9f9")
        self.Label2.configure(activeforeground="black")
        self.Label2.configure(background="#d9d9d9")
        self.Label2.configure(disabledforeground="#a3a3a3")
        self.Label2.configure(foreground="#000000")
        self.Label2.configure(highlightbackground="#d9d9d9")
        self.Label2.configure(highlightcolor="black")
        self.Label2.configure(text='''Select the robots required then click Ok''')

        self.Button1 = Button(self.top)
        self.Button1.place(relx=0.28, rely=0.8, height=24, width=57)
        self.Button1.configure(activebackground="#d9d9d9")
        self.Button1.configure(activeforeground="#000000")
        self.Button1.configure(background="#d9d9d9")
        self.Button1.configure(command=self.okButton)
        self.Button1.configure(disabledforeground="#a3a3a3")
        self.Button1.configure(foreground="#000000")
        self.Button1.configure(highlightbackground="#d9d9d9")
        self.Button1.configure(highlightcolor="black")
        self.Button1.configure(pady="0")
        self.Button1.configure(text='''Ok''')

        self.Button2 = Button(self.top)
        self.Button2.place(relx=0.61, rely=0.8, height=24, width=47)
        self.Button2.configure(activebackground="#d9d9d9")
        self.Button2.configure(activeforeground="#000000")
        self.Button2.configure(background="#d9d9d9")
        self.Button2.configure(command=self.cancelButton)
        self.Button2.configure(disabledforeground="#a3a3a3")
        self.Button2.configure(foreground="#000000")
        self.Button2.configure(highlightbackground="#d9d9d9")
        self.Button2.configure(highlightcolor="black")
        self.Button2.configure(pady="0")
        self.Button2.configure(text='''Cancel''')

        self.top.wait_window()

    def okButton(self):
        selected=self.RobotList.curselection()
        if selected==():
            if messagebox.askyesno("Ok","No robots selected.Quit?"):
                self.top.destroy()
            else:
                return
        self.chosenBotList=[]
        for idx in selected:
            self.chosenBotList.append(self.RobotList.get(idx))

        self.top.destroy()

    def cancelButton(self):
        self.on_closing()

    def on_closing(self):
        if messagebox.askyesno("Quit", "Are you sure you want to close this dialog?"):
            self.top.destroy()

    def getList(self):
        return self.chosenBotList



# The following code is added to facilitate the Scrolled widgets you specified.
class AutoScroll(object):
    '''Configure the scrollbars for a widget.'''

    def __init__(self, master):
        #  Rozen. Added the try-except clauses so that this class
        #  could be used for scrolled entry widget for which vertical
        #  scrolling is not supported. 5/7/14.
        try:
            vsb = ttk.Scrollbar(master, orient='vertical', command=self.yview)
        except:
            pass
        hsb = ttk.Scrollbar(master, orient='horizontal', command=self.xview)

        #self.configure(yscrollcommand=_autoscroll(vsb),
        #    xscrollcommand=_autoscroll(hsb))
        try:
            self.configure(yscrollcommand=self._autoscroll(vsb))
        except:
            pass
        self.configure(xscrollcommand=self._autoscroll(hsb))

        self.grid(column=0, row=0, sticky='nsew')
        try:
            vsb.grid(column=1, row=0, sticky='ns')
        except:
            pass
        hsb.grid(column=0, row=1, sticky='ew')

        master.grid_columnconfigure(0, weight=1)
        master.grid_rowconfigure(0, weight=1)

        # Copy geometry methods of master  (taken from ScrolledText.py)
        if py3:
            methods = Pack.__dict__.keys() | Grid.__dict__.keys() \
                  | Place.__dict__.keys()
        else:
            methods = Pack.__dict__.keys() + Grid.__dict__.keys() \
                  + Place.__dict__.keys()

        for meth in methods:
            if meth[0] != '_' and meth not in ('config', 'configure'):
                setattr(self, meth, getattr(master, meth))

    @staticmethod
    def _autoscroll(sbar):
        '''Hide and show scrollbar as needed.'''
        def wrapped(first, last):
            first, last = float(first), float(last)
            if first <= 0 and last >= 1:
                sbar.grid_remove()
            else:
                sbar.grid()
            sbar.set(first, last)
        return wrapped

    def __str__(self):
        return str(self.master)

def _create_container(func):
    '''Creates a ttk Frame with a given master, and use this new frame to
    place the scrollbars and the widget.'''
    def wrapped(cls, master, **kw):
        container = ttk.Frame(master)
        return func(cls, container, **kw)
    return wrapped

class ScrolledListBox(AutoScroll, Listbox):
    '''A standard Tkinter Text widget with scrollbars that will
    automatically show/hide as needed.'''
    @_create_container
    def __init__(self, master, **kw):
        Listbox.__init__(self, master, **kw)
        AutoScroll.__init__(self, master)

if __name__ == '__main__':
    root=Tk()
    rc=RobotChooser(root,"..\\robot.json")
    rc.show()
    botList=rc.getList()

    print("CHOSEN BOTLIST=",botList)

