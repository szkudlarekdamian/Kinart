from tkinter import *
#import tkFileDialog
#from tkinter.colorchooser import askcolor
from PIL import Image


class Paint(object):

    DEFAULT_PEN_SIZE = 5.0
    DEFAULT_COLOR = 'black'

    def __init__(self):
        self.root = Tk()

        # PEN BUTTON
        self.pen_button = Button(self.root, text='PEN', height=3, width=7, command=self.use_pen)
        self.pen_button.grid(row=0, column=0)

        # ERASER BUTTON
        self.eraser_button = Button(self.root, text='eraser', height=3, width=7, command=self.use_eraser)
        self.eraser_button.grid(row=0, column=1)

        # 4 COLORS
        self.color_button = Button(self.root, bg='green', height=3, width=7, command=self.green_color)
        self.color_button.grid(row=0, column=2)
        self.color_button = Button(self.root, bg='red', height=3, width=7, command=self.red_color)
        self.color_button.grid(row=0, column=3)
        self.color_button = Button(self.root, bg='blue', height=3, width=7, command=self.blue_color)
        self.color_button.grid(row=0, column=4)
        self.color_button = Button(self.root, bg='black', height=3, width=7, command=self.black_color)
        self.color_button.grid(row=0, column=5)

        # PAINTING
        self.c = Canvas(self.root, bg='white', width=600, height=500)
        self.c.grid(row=1, columnspan=6)

        # SAVE IMAGE
        #self.save_button = Button(self.root, bg='black', height=3, width=7, command=self.save)
        #self.save_button.grid(row=2, columnspan=6)

        self.setup()
        self.root.mainloop()

    #def save(self):
    #    self.filename = tkFileDialog.asksaveasfilename(initialdir="/", title="Select file",
    #                                                   filetypes=(("jpeg files", "*.jpg"), ("all files", "*.*")))

    def setup(self):
        self.old_x = None
        self.old_y = None
        self.line_width = 20
        self.color = self.DEFAULT_COLOR
        self.eraser_on = False
        self.active_button = self.pen_button
        self.c.bind('<B1-Motion>', self.paint)
        self.c.bind('<ButtonRelease-1>', self.reset)

    def use_pen(self):
        self.activate_button(self.pen_button)

    def use_brush(self):
        self.activate_button(self.brush_button)

    def green_color(self):
        self.eraser_on = False
        self.color = 'green'

    def red_color(self):
        self.eraser_on = False
        self.color = 'red'

    def blue_color(self):
        self.eraser_on = False
        self.color = 'blue'

    def black_color(self):
        self.eraser_on = False
        self.color = 'black'

    def use_eraser(self):
        self.activate_button(self.eraser_button, eraser_mode=True)

    def activate_button(self, some_button, eraser_mode=False):
        self.active_button.config(relief=RAISED)
        some_button.config(relief=SUNKEN)
        self.active_button = some_button
        self.eraser_on = eraser_mode

    def paint(self, event):
        self.line_width = 20.0 if self.eraser_on else 5.0
        paint_color = 'white' if self.eraser_on else self.color
        if self.old_x and self.old_y:
            self.c.create_line(self.old_x, self.old_y, event.x, event.y,
                               width=self.line_width, fill=paint_color,
                               capstyle=ROUND, smooth=TRUE, splinesteps=36)

        self.old_x = event.x
        self.old_y = event.y

    def reset(self, event):
        self.old_x, self.old_y = None, None


if __name__ == '__main__':
    Paint()
