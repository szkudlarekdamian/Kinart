import tkinter as tk
import time
import pyautogui

class Kinart(object):

    DEFAULT_PEN_SIZE = 5.0
    DEFAULT_COLOR = 'black'

    def __init__(self):
        self.root = tk.Tk()
        self.root.lift() # always on the top

        # WINDOW SIZE
        sheight, swidth = self.root.winfo_screenheight(), self.root.winfo_screenwidth()
        self.root.geometry('{}x{}'.format(swidth,sheight))

        # PEN BUTTON
        self.pen_button = tk.Button(self.root, text='PEN', height=3, width=7, command=self.use_pen)
        self.pen_button.grid(row=0, column=0, sticky='NSEW')

        # ERASER BUTTON
        self.eraser_button = tk.Button(self.root, text='eraser', height=3, width=7, command=self.use_eraser)
        self.eraser_button.grid(row=0, column=1, sticky='NSEW')

        # 4 COLORS
        self.color_button1 = tk.Button(self.root, bg='green', height=3, width=7, command=self.green_color)
        self.color_button1.grid(row=0, column=2, sticky='NSEW')
        self.color_button2 = tk.Button(self.root, bg='red', height=3, width=7, command=self.red_color)
        self.color_button2.grid(row=0, column=3, sticky='NSEW')
        self.color_button3 = tk.Button(self.root, bg='blue', height=3, width=7, command=self.blue_color)
        self.color_button3.grid(row=0, column=4, sticky='NSEW')
        self.color_button4 = tk.Button(self.root, bg='black', height=3, width=7, command=self.black_color)
        self.color_button4.grid(row=0, column=5, sticky='NSEW')

        # PAINTING
        self.painting = tk.Canvas(self.root, bg='white')
        self.painting.grid(row=1, columnspan=6, sticky='NSEW')

        # AUTORESIZE ELEMENTS
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=1)
        self.root.grid_columnconfigure(3, weight=1)
        self.root.grid_columnconfigure(4, weight=1)
        self.root.grid_columnconfigure(5, weight=1)
        self.root.grid_rowconfigure(0, weight=0)
        self.root.grid_rowconfigure(1, weight=1)

        #bx, by = self.color_button1.event_generate(), self.color_button1.winfo_rooty()
        #bw, bh = self.color_button1.winfo_width(), self.color_button1.winfo_height()
        #print(str(bx) + ', ' + str(by))
        #print(str(bw) + ', ' + str(bw))

        self.setup()

        while True:
            for x in range(115,714):
                pyautogui.moveTo(x,690)
                pyautogui.mouseDown(button='left')
                self.root.update()

            #mx, my = pyautogui.position()
            #bx, cy = self.color_button1.winfo_rootx(), self.color_button1.winfo_rooty()
            #bw, bh = self.color_button1.winfo_width(), self.color_button1.winfo_height()
            #self.root.update()

        self.root.mainloop()

    def setup(self):
        self.ispainting = False
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
        self.active_button_color.config(relief=tk.RAISED)
        self.activate_button(self.eraser_button, eraser_mode=True)

    def activate_button(self, some_button, eraser_mode=False):
        self.active_button.config(relief=tk.RAISED) # border decoration
        some_button.config(relief=tk.SUNKEN)
        self.active_button = some_button
        self.eraser_on = eraser_mode

    def activate_button_color(self, some_button, eraser_mode=False):
        self.active_button_color.config(relief=tk.RAISED) # border decoration
        some_button.config(relief=tk.SUNKEN)
        self.active_button_color = some_button
        self.eraser_on = eraser_mode
        self.activate_button(self.pen_button)

    def paint(self, event):
        self.line_width = 20.0 if self.eraser_on else 5.0
        paint_color = 'white' if self.eraser_on else self.color
        if self.old_x and self.old_y:
            self.painting.create_line(self.old_x, self.old_y, event.x, event.y,
                               width=self.line_width, fill=paint_color,
                               capstyle=tk.ROUND, smooth=tk.TRUE, splinesteps=36)
        self.old_x = event.x
        self.old_y = event.y
        #print(str(self.old_x))
        #print(str(x))
        #print('The current pointer position is {0}'.format(position))

    def reset(self, event):
        self.old_x = None
        self.old_y = None


if __name__ == '__main__':
    Kinart()
