from tkinter import *

class Kinart(object):

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
        self.color_button1 = Button(self.root, bg='green', height=3, width=7, command=self.green_color)
        self.color_button1.grid(row=0, column=2)
        self.color_button2 = Button(self.root, bg='red', height=3, width=7, command=self.red_color)
        self.color_button2.grid(row=0, column=3)
        self.color_button3 = Button(self.root, bg='blue', height=3, width=7, command=self.blue_color)
        self.color_button3.grid(row=0, column=4)
        self.color_button4 = Button(self.root, bg='black', height=3, width=7, command=self.black_color)
        self.color_button4.grid(row=0, column=5)

        # PAINTING
        self.painting = Canvas(self.root, bg='white', width=600, height=500)
        self.painting.grid(row=1, columnspan=6)

        self.setup()
        self.root.mainloop()

    def setup(self):
        self.old_x = None
        self.old_y = None
        self.line_width = 20
        self.color = self.DEFAULT_COLOR
        self.eraser_on = False
        self.active_button = self.pen_button
        self.activate_button(self.active_button)
        self.active_button_color = self.color_button4
        self.activate_button_color(self.active_button_color)
        self.painting.bind('<B1-Motion>', self.paint) # event format - the left button is being held down
        self.painting.bind('<ButtonRelease-1>', self.reset)

    def use_pen(self):
        self.activate_button(self.pen_button)

    def green_color(self):
        self.eraser_on = False
        self.color = 'green'
        self.activate_button_color(self.color_button1)

    def red_color(self):
        self.eraser_on = False
        self.color = 'red'
        self.activate_button_color(self.color_button2)

    def blue_color(self):
        self.eraser_on = False
        self.color = 'blue'
        self.activate_button_color(self.color_button3)

    def black_color(self):
        self.eraser_on = False
        self.color = 'black'
        self.activate_button_color(self.color_button4)

    def use_eraser(self):
        self.active_button_color.config(relief=RAISED)
        self.activate_button(self.eraser_button, eraser_mode=True)

    def activate_button(self, some_button, eraser_mode=False):
        self.active_button.config(relief=RAISED) # border decoration
        some_button.config(relief=SUNKEN)
        self.active_button = some_button
        self.eraser_on = eraser_mode

    def activate_button_color(self, some_button, eraser_mode=False):
        self.active_button_color.config(relief=RAISED) # border decoration
        some_button.config(relief=SUNKEN)
        self.active_button_color = some_button
        self.eraser_on = eraser_mode
        self.activate_button(self.pen_button)

    def paint(self, event):
        self.line_width = 20.0 if self.eraser_on else 5.0
        paint_color = 'white' if self.eraser_on else self.color
        if self.old_x and self.old_y:
            self.painting.create_line(self.old_x, self.old_y, event.x, event.y,
                               width=self.line_width, fill=paint_color,
                               capstyle=ROUND, smooth=TRUE, splinesteps=36)
        self.old_x = event.x
        self.old_y = event.y

    def reset(self, event):
        self.old_x, self.old_y = None, None


if __name__ == '__main__':
    Kinart()
