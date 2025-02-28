import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import math
import numpy as np

class LayerRenderer:
    def __init__(self):
        self.__bg_mipmap = []
        self.__fg_mipmap = []
        self.fg_opacity = 1.0
        self.__blended_render = None

        self.__shift = [0, 0]

        self.current_fg = None
        
    def get_render(self):
        return self.__blended_render, self.__shift

    def __build_mipmap(self, image):
        pyramid = [image]
        while pyramid[-1].width > 512 and pyramid[-1].height > 512:
            new_img = pyramid[-1].resize(
                (pyramid[-1].width // 2, pyramid[-1].height // 2), Image.BILINEAR
            )
            pyramid.append(new_img)
        return pyramid

    def load_background(self, filename):
        if not self.__fg_mipmap:
            print("Load the foreground first")
            return

        image = Image.open(filename).convert("RGB")
        if image.size != self.__fg_mipmap[0].size:
            print("foreground and background images have different size. resizing background image")
            image = image.resize(self.__fg_mipmap[0].size, Image.BILINEAR)
            
        self.__bg_mipmap = self.__build_mipmap(image)


    def load_foreground(self, filename):
        self.current_fg = Image.open(filename).convert("RGB")
        self.__fg_mipmap = self.__build_mipmap(self.current_fg)
        self.__bg_mipmap = []

    def set_opacity(self, opacity):
        self.fg_opacity = opacity
                

    def __render_foreground(self, region_box, new_width, new_height, mipmap_level):
        if not self.__fg_mipmap:
            return

        fg_img = self.__fg_mipmap[mipmap_level].crop(region_box)
        return fg_img.resize((new_width, new_height), Image.BILINEAR)

    def __render_background(self, region_box, new_width, new_height, mipmap_level):
        if not self.__bg_mipmap:
            return

        bg_img = self.__bg_mipmap[mipmap_level].crop(region_box)
        return bg_img.resize((new_width, new_height), Image.BILINEAR)

    def __blend_layers(self, fg, bg):
        # Ensure both renders are available.
        if fg is not None:
            if bg is not None:
                bg_np = np.array(bg).astype(np.float32)
                fg_np = np.array(fg).astype(np.float32)
        
                blended_np = bg_np * (1 - self.fg_opacity) + fg_np * self.fg_opacity
                blended_np = np.clip(blended_np, 0, 255).astype(np.uint8)
                blended_img = Image.fromarray(blended_np)
                self.__blended_render = ImageTk.PhotoImage(blended_img)

            else:
                fg_np = np.array(fg).astype(np.float32)
                blended_np = fg_np * self.fg_opacity
                blended_np = np.clip(blended_np, 0, 255).astype(np.uint8)
                blended_img = Image.fromarray(blended_np)
                self.__blended_render = ImageTk.PhotoImage(blended_img)

            

    
    def render(self, orig_top_left, orig_bottom_right, scale):
                
        if not self.__fg_mipmap:
            return

        self.__fg_render = None
        self.__bg_render = None
        self.__blended_render = None
        
        total_levels = len(self.__fg_mipmap)

        if scale >= 1.0:
            selected_level = 0
        else:
            selected_level = min(-int(math.log(scale, 2)), total_levels - 1)

        effective_scale = scale * (2 ** selected_level)
        selected_top_left = orig_top_left / (2 ** selected_level)
        selected_bottom_right = orig_bottom_right / (2 ** selected_level)

        selected_width = self.__fg_mipmap[selected_level].width
        selected_height = self.__fg_mipmap[selected_level].height

        clamped_top_left = [max(selected_top_left[0], 0), max(selected_top_left[1], 0)]
        clamped_bottom_right = [
            min(selected_bottom_right[0], selected_width),
            min(selected_bottom_right[1], selected_height)
        ]

        shift_x = (clamped_top_left[0] - selected_top_left[0]) * effective_scale
        shift_y = (clamped_top_left[1] - selected_top_left[1]) * effective_scale

        self.__shift = [shift_x, shift_y]
        
        new_width = int((clamped_bottom_right[0] - clamped_top_left[0]) * effective_scale)
        new_height = int((clamped_bottom_right[1] - clamped_top_left[1]) * effective_scale)

        if new_width < 1 or new_height < 1:
            return

        region_box = (
            int(clamped_top_left[0]), int(clamped_top_left[1]),
            int(clamped_bottom_right[0]), int(clamped_bottom_right[1])
        )

        
        fg_render = self.__render_foreground(region_box, new_width, new_height, selected_level)
        
        bg_render = self.__render_background(region_box, new_width, new_height, selected_level)
        
        self.__blend_layers(fg_render, bg_render)
        
