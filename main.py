#!/usr/bin/python3

import tkinter as tk
from MainGUI import MainGUI

if __name__ == '__main__':
    root = tk.Tk()
    root.title("Photogrammetry labeller")
    root.geometry("800x600")
    root.minsize(800, 700)
    app = MainGUI(root)  # start the application
    app.pack(fill="both", expand = True)
    root.mainloop()
    #app.mainloop()  # application is up and running

