from tkinter import *
import time

class ToolTip(object):

    def __init__(self, widget, text):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0
        self.text = text

    def showtip(self):
        "Display text in tooltip window"
        if self.has_focus:
            if self.tipwindow or not self.text:
                return
            x, y, cx, cy = self.widget.bbox("insert")
            # x = x + self.widget.winfo_rootx() + 57
            # y = y + cy + self.widget.winfo_rooty() +27
            x = x + self.widget.winfo_pointerx() + 15
            y = y + cy + self.widget.winfo_pointery() +5
            self.tipwindow = tw = Toplevel(self.widget)
            tw.wm_overrideredirect(1)
            tw.wm_geometry("+%d+%d" % (x, y))
            label = Label(tw, text=self.text, justify=LEFT,
                          background="#ffffe0", relief=SOLID, borderwidth=1,
                          font=("tahoma", "8", "normal"))
            label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

def CreateToolTip(widget, text):
    toolTip = ToolTip(widget, text)
    def enter(event):
        toolTip.has_focus = True
        widget.after(1000, toolTip.showtip)
        #toolTip.showtip(text)
    def leave(event):
        toolTip.has_focus = False
        toolTip.hidetip()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)
