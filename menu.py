import tkinter as tk
import GUI as g

class Menu(object):

    def __init__(self):
        self.menuwindow = tk.Tk()
        self.menuwindow.lift() # always on the top

        width = 400
        height = 300

        self.f = tk.Frame(self.menuwindow, bg="green", width=width, height=height)
        self.f.grid(row=0, column=0, sticky="NW")
        self.f.grid_propagate(0)
        self.f.update()

        self.tytul = tk.Label(self.f, text="KINART", fg="yellow", font=("Arial", 70), bg="green")
        self.tytul.place(x=width/2, y=height/3, anchor="center")

        self.start_button = tk.Button(self.f, text='START', font=("Arial", 30), command=self.open_kinart)
        self.start_button.place(x=width/2, y=(height/3)*2, anchor="center")

        self.menuwindow.update()
        self.menuwindow.mainloop()

    def open_kinart(self):
        paint = g.Kinart()

if __name__ == "__main__":
    Menu()