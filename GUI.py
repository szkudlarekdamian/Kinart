import tkinter as tk
import time
import pyautogui
import handTracker as ht
import cv2

class Kinart(object):

    DEFAULT_PEN_SIZE = 5.0
    DEFAULT_COLOR = 'black'

    def __init__(self):
        self.root = tk.Tk()
        self.root.lift() # always on the top

        # WINDOW SIZE
        sheight, swidth = self.root.winfo_screenheight(), self.root.winfo_screenwidth()
        #self.root.geometry('{}x{}'.format(swidth,sheight))
        self.root.geometry('600x600')

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

        self.setup()

        #while True:
        #    for x in lista:
        #        time.sleep(0.1)
        #        if self.old_x and self.old_y:
        #            self.painting.create_line( self.old_x, self.old_y, x[0], x[1], width=self.line_width,
        #                               fill=self.color, capstyle=tk.ROUND, smooth=tk.TRUE, splinesteps=36)
        #        self.old_x = x[0]
        #        self.old_y = x[1]
        #    #pyautogui.moveTo(x, y)
        #    #pyautogui.mouseDown(button='left')
        #        self.root.update()
        #    self.root.update()

        #self.root.mainloop()

    def updateCoords(self, x, y):
        time.sleep(0.1)
        if self.old_x and self.old_y:
            self.painting.create_line(self.old_x, self.old_y, x, y, width=self.line_width,
                                      fill=self.color, capstyle=tk.ROUND, smooth=tk.TRUE, splinesteps=36)
        self.old_x = x
        self.old_y = y
        self.root.update()

    def setup(self):
        self.ispainting = False
        self.old_x = 0
        self.old_y = 0
        self.line_width = 20
        self.color = self.DEFAULT_COLOR
        self.eraser_on = False
        self.active_button = self.pen_button
        self.activate_button(self.active_button)
        self.active_button_color = self.color_button4
        self.activate_button_color(self.active_button_color)
        #self.painting.bind('<B1-Motion>', self.paint) # event format - the left button is being held down
        #self.painting.bind('<ButtonRelease-1>', self.reset)

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

    def paint(self,event):
        self.line_width = 20.0 if self.eraser_on else 5.0
        paint_color = 'white' if self.eraser_on else self.color
        if self.old_x and self.old_y:
            self.painting.create_line(self.old_x, self.old_y, event.x, event.y,
                               width=self.line_width, fill=paint_color,
                               capstyle=tk.ROUND, smooth=tk.TRUE, splinesteps=36)
        self.old_x = event.x
        self.old_y = event.y

    def reset(self, event):
        self.old_x = None
        self.old_y = None

if __name__ == '__main__':
    #paint = Kinart()

    # Ścieżka do filmu z mapą głębi lub ID kamery
    videoPath = "C:\\Users\\marce\\Desktop\\videokinec_depth4_v2.avi"

    # Obiekt klasy HandTracker, której głównym zadaniem jest zwracanie współrzędnych dłoni, na podstawie filmu mapy głębi
    hT = ht.HandTracker(videoPath)
    # Obiekt klasy Kinart - rysowanie
    paint = Kinart()

    while (hT.kinectOpened()):
        # Sztuczne spowolnienie klatek, tylko do celów testowych
        #time.sleep(0.1)
        # Pobieranie kolejnej klatki
        frame = hT.getNextFrame()
        # Jeśli klatka została wczytana poprawnie to kontynuuj
        if frame is not None:
            # Jeśli dłoń nie została jeszcze zainicjalizowana do systemu
            if hT.handInitialized is False:
                # Pokaż klatkę z narysowaną przestrzenią na dłoń
                cv2.imshow('Kinart', hT.getFrameWithInitBox(frame))
                # Jeśli wciśnięto 'z' to rozpocznij inicjalizację dłoni
                if cv2.waitKey(1) == ord('z'):
                    hT.initTracker(frame)
                    hT.handInitialized = True
            # Jeśli dłoń została zainicjalizowana to
            else:
                # Śledź dłoń i uzyskaj jej współrzędne
                frameWithCoords, coords = hT.trackHand(frame)
                cv2.imshow('Kinart', frameWithCoords)
                cv2.waitKey(1)
                if coords != None:
                    paint.updateCoords(coords[0],coords[1])
        else:
            break

    paint.root.mainloop()
