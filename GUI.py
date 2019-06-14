import tkinter as tk
import PIL
from PIL import ImageDraw

class Kinart(object):

    def __init__(self):
        self.root = tk.Tk()
        self.root.lift()

        # WINDOW SIZE
        self.root.geometry('640x480')

        # PEN BUTTON
        self.pen_button = tk.Button(self.root, text='PEN', bg='green', height=3, width=5, command=self.use_pen)
        self.pen_button.grid(row=0, column=0, sticky='NSEW')

        # ERASER BUTTON
        self.eraser_button = tk.Button(self.root, text='ERASER', bg='green', height=3, width=5, command=self.use_eraser)
        self.eraser_button.grid(row=0, column=1, sticky='NSEW')

        # 4 COLORS
        self.green_button = tk.Button(self.root, bg='green', height=3, width=5, command=self.green_color)
        self.green_button.grid(row=0, column=2, sticky='NSEW')

        self.red_button = tk.Button(self.root, bg='red', height=3, width=5, command=self.red_color)
        self.red_button.grid(row=0, column=3, sticky='NSEW')

        self.blue_button = tk.Button(self.root, bg='blue', height=3, width=5, command=self.blue_color)
        self.blue_button.grid(row=0, column=4, sticky='NSEW')

        self.black_button = tk.Button(self.root, bg='black', height=3, width=5, command=self.black_color)
        self.black_button.grid(row=0, column=5, sticky='NSEW')

        # SAVE BUTTON
        self.save_button = tk.Button(self.root, text="SAVE", bg='green', height=3, width=5, command=self.save)
        self.save_button.grid(row=0, column=6, sticky='NSEW')

        # PAINTING
        self.painting = tk.Canvas(self.root, bg='white')
        self.painting.grid(row=1, columnspan=7, sticky='NSEW')

        # PAINTING TO SAVE
        self.image = PIL.Image.new("RGB", (640,430), (255, 255, 255))
        self.draw = ImageDraw.Draw(self.image)

        # AUTORESIZE ELEMENTS
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=1)
        self.root.grid_columnconfigure(3, weight=1)
        self.root.grid_columnconfigure(4, weight=1)
        self.root.grid_columnconfigure(5, weight=1)
        self.root.grid_columnconfigure(6, weight=1)
        self.root.grid_rowconfigure(0, weight=0)
        self.root.grid_rowconfigure(1, weight=1)

        self.root.update()
        self.setup()

    def setup(self):
        self.old_x = 0
        self.old_y = 0
        self.old_dot = None
        self.line_width = 20
        self.color = 'black'
        self.eraser_on = False
        self.active_button = self.pen_button
        self.activate_button(self.active_button)
        self.active_button_color = self.black_button
        self.activate_button_color(self.active_button_color)

    def updateCoords(self, x, y):
        self.line_width = 20 if self.eraser_on else 5
        paint_color = 'white' if self.eraser_on else self.color
        if self.old_x and self.old_y:
            self.painting.create_line(self.old_x, self.old_y, x, y, width=self.line_width, fill=paint_color, capstyle=tk.ROUND, smooth=tk.TRUE, splinesteps=36)
            self.draw.line([self.old_x, self.old_y, x, y], width=self.line_width, fill=paint_color)
        self.old_x = x
        self.old_y = y
        self.root.update()

    def resetCoords(self):
        self.old_x = None
        self.old_y = None

    def createDot(self, x, y):
        if self.old_dot:
            self.painting.delete(self.old_dot)
            self.root.update()
        dot = self.painting.create_oval(x, y, x+15, y+15, width=10.0, fill=self.color)
        self.old_dot = dot
        self.root.update()

    def resetDot(self):
        if self.old_dot:
            self.painting.delete(self.old_dot)
            self.root.update()

    def use_pen(self):
        self.active_button_color.config(relief=tk.SUNKEN)
        self.activate_button(self.pen_button)

    def use_eraser(self):
        self.active_button_color.config(relief=tk.RAISED)
        self(self.eraser_button, eraser_mode=True)

    def green_color(self):
        self.eraser_on = False
        self.color = 'green'
        self.activate_button_color(self.green_button)

    def red_color(self):
        self.eraser_on = False
        self.color = 'red'
        self.activate_button_color(self.red_button)

    def blue_color(self):
        self.eraser_on = False
        self.color = 'blue'
        self.activate_button_color(self.blue_button)

    def black_color(self):
        self.eraser_on = False
        self.color = 'black'
        self.activate_button_color(self.black_button)

    def activate_button(self, some_button, eraser_mode=False):
        self.active_button.config(relief=tk.RAISED)
        self.active_button = some_button
        some_button.config(relief=tk.SUNKEN)
        self.eraser_on = eraser_mode

    def activate_button_color(self, some_button, eraser_mode=False):
        self.active_button_color.config(relief=tk.RAISED)
        some_button.config(relief=tk.SUNKEN)
        self.active_button_color = some_button
        self.eraser_on = eraser_mode
        self.activate_button(self.pen_button)

    def save(self):
        self.active_button_color.config(relief=tk.RAISED)
        self.activate_button(self.save_button)
        filename = "painting.jpg"
        self.image.save(filename)

if __name__ == "__main__":
    Kinart()