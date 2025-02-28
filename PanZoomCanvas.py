import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import math
import numpy as np

class PanZoomCanvas(tk.Canvas):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.__scale = 1.0          # Overall zoom factor.
        self.__offset = np.array([0.0, 0.0])  # Offset: canvas coordinate of image’s top-left.
        #self.__coord_callback = None  # Function to update coordinate display.
        self.__render_callback = None  # Callback for external drawing.
        self.__pan_start = None      # Starting point for panning.

        self.__register_actions()
        parent.bind("<Configure>", self.__on_resize)
        
    def __register_actions(self):
        self.bind("<MouseWheel>", self.__on_mousewheel)  # windows/mac scroll.
        self.bind("<Button-4>", self.__on_mousewheel)  # Linux scroll up.
        self.bind("<Button-5>", self.__on_mousewheel)  # Linux scroll down.
        self.bind("<Button-2>", self.__start_pan)        # Middle-click to start panning.
        self.bind("<B2-Motion>", self.__do_pan)          # Drag for panning.
        
        
    def bind_rendering_system(self, rendering_function):
        self.__render_callback = rendering_function

    def bind_coord_callback(self, coord_callback):
        self.__coord_callback = coord_callback
        
    def register_left_button_click(self, callback_function):
        self.left_mouse_click_callback = callback_function
        self.bind("<ButtonPress-1>", self.__on_left_click)

    def register_left_button_release(self, callback_function):
        print("registered left button release")
        self.left_mouse_release_callback = callback_function
        self.bind("<ButtonRelease-1>", self.__on_left_release)

    def register_left_button_drag(self, callback_function):
        self.left_mouse_drag_callback = callback_function
        self.bind("<B1-Motion>", self.__on_left_drag)

    def register_right_button_click(self, callback_function):
        self.right_mouse_click_callback = callback_function
        self.bind("<Button-3>", self.__on_right_click)

    def register_mouse_move(self, callback_function):
        self.mouse_move_callback = callback_function
        self.bind("<Motion>", self.__on_mouse_move)  # Update coordinate label.
        
    def register_del_key(self, callback_function):
        print("delete binding set")
        self.__delete_callback = callback_function
        self.bind("<Delete>", self.__delete_callback)
        
        
    def __on_left_click(self, event):
        event.widget.focus_set()
        if hasattr(self, 'left_mouse_click_callback'):
            self.left_mouse_click_callback(self.canvasx(event.x), self.canvasy(event.y))

    def __on_left_release(self, event):
        if hasattr(self, 'left_mouse_release_callback'):
            self.left_mouse_release_callback(self.canvasx(event.x), self.canvasy(event.y))

            
    def __on_left_drag(self, event):
        if hasattr(self, 'left_mouse_drag_callback'):
            self.left_mouse_drag_callback(self.canvasx(event.x), self.canvasy(event.y))

    def __on_mouse_move(self, event):
        if hasattr(self, 'mouse_move_callback'):
            self.mouse_move_callback(self.canvasx(event.x), self.canvasy(event.y))

            
    def __on_right_click(self, event):
        if hasattr(self, 'right_mouse_click_callback'):
            self.right_mouse_click_callback(self.canvasx(event.x), self.canvasy(event.y))

    def __redraw_image(self):
        if self.__render_callback is None:
            return
        visible_width = self.winfo_width()
        visible_height = self.winfo_height()
        if visible_width < 2 or visible_height < 2:
            self.after(100, self.__redraw_image)
            return
        # Get visible region in canvas coordinates.
        top_left = np.array([self.canvasx(0), self.canvasy(0)])
        bottom_right = np.array([self.canvasx(visible_width), self.canvasy(visible_height)])
        # Convert to original image coordinates.
        orig_top_left = self.screen_to_orig_image_coord(top_left)
        orig_bottom_right = self.screen_to_orig_image_coord(bottom_right)
        self.__render_callback(orig_top_left, orig_bottom_right, self.__scale)

    def redraw(self):
        self.__redraw_image()
                
    def __on_mousewheel(self, event):
        min_scale = 0.025
        max_scale = 16.0
        if event.num == 5 or event.delta == -120:
            scale_factor = 0.5 if self.__scale > min_scale else 1.0
        elif event.num == 4 or event.delta == 120:
            scale_factor = 2.0 if self.__scale < max_scale else 1.0
        else:
            scale_factor = 1.0
        if scale_factor != 1.0:
            screen_coord = np.array([self.canvasx(event.x), self.canvasy(event.y)])
            orig_coord = self.screen_to_orig_image_coord(screen_coord)
            self.__scale *= scale_factor
            self.__offset = orig_coord * self.__scale - screen_coord
            self.__redraw_image()

    def __start_pan(self, event):
        self.__pan_start = (event.x, event.y)

    def __do_pan(self, event):
        if self.__pan_start is None:
            return
        dx = event.x - self.__pan_start[0]
        dy = event.y - self.__pan_start[1]
        self.__pan_start = (event.x, event.y)
        self.__offset += np.array([-dx, -dy])
        self.__redraw_image()


    def __on_resize(self, event):
        self.after(50, self.__redraw_image)

    def screen_to_orig_image_coord(self, screen_coord):
        return (screen_coord + self.__offset) / self.__scale

    def orig_image_to_screen(self, orig_coord):
        return orig_coord*self.__scale - self.__offset 

    def reset(self):
        self.__scale = 1.0
        self.__offset = np.array([0.0, 0.0])
        self.__pan_start = None
        self.__redraw_image()
