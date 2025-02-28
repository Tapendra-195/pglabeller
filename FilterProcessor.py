import cv2
import numpy as np
import math
from PIL import Image, ImageTk

class FilterProcessor:
    def __init__(self):
        self.__image_mipmap = None
        self.__updated = False
        self.__d = 0
        self.__sigma_color = 0
        self.__sigma_space = 0
        self.__original_image = None
        self.__render_image = None
        self.__shift = None
        
    def get_render(self):
        return self.__render_image, self.__shift

    def bind_image(self, image):
        self.__original_image = image
        self.__updated = True


    def render(self, orig_top_left, orig_bottom_right, scale):
        if self.__original_image is None:
            print("Bind image before rendering")
            return

        if self.__updated:
            # Apply filter if the image is updated
            self.__apply_filter()
            self.__updated = False
            
        # Display image using the mipmap
        total_levels = len(self.__image_mipmap)

        if scale >= 1.0:
            selected_level = 0
        else:
            selected_level = min(-int(math.log(scale, 2)), total_levels - 1)

        effective_scale = scale * (2 ** selected_level)
        selected_top_left = [orig_top_left[0] / (2 ** selected_level), orig_top_left[1] / (2 ** selected_level)]
        selected_bottom_right = [orig_bottom_right[0] / (2 ** selected_level), orig_bottom_right[1] / (2 ** selected_level)]

        selected_width = self.__image_mipmap[selected_level].width
        selected_height = self.__image_mipmap[selected_level].height

        clamped_top_left = [max(selected_top_left[0], 0), max(selected_top_left[1], 0)]
        clamped_bottom_right = [
            min(selected_bottom_right[0], selected_width),
            min(selected_bottom_right[1], selected_height)
        ]

        shift_x = (clamped_top_left[0] - selected_top_left[0]) * effective_scale
        shift_y = (clamped_top_left[1] - selected_top_left[1]) * effective_scale

        new_width = int((clamped_bottom_right[0] - clamped_top_left[0]) * effective_scale)
        new_height = int((clamped_bottom_right[1] - clamped_top_left[1]) * effective_scale)

        if new_width < 1 or new_height < 1:
            return

        region_box = (
            int(clamped_top_left[0]), int(clamped_top_left[1]),
            int(clamped_bottom_right[0]), int(clamped_bottom_right[1])
        )

        # Correct reference: using __image_mipmap
        img = self.__image_mipmap[selected_level].crop(region_box)
        img = img.resize((new_width, new_height), Image.BILINEAR)

        self.__render_image = ImageTk.PhotoImage(img)

        self.__shift = [shift_x, shift_y]


    #returns bw image to blob detector    
    def get_current_image(self):
        if self.__updated:
            self.__apply_filter()

        # Convert the top-level image to grayscale using OpenCV
        gray_image = cv2.cvtColor(np.array(self.__image_mipmap[0]), cv2.COLOR_RGB2GRAY)
        return gray_image
            
    def set_d(self, value):
        value = int(value)
        if value != self.__d:
            self.__updated = True
            self.__d = int(value)
            print("d = ",self.__d)
        
    def set_sigma_color(self, value):
        value = int(value)
        if value != self.__sigma_color:
            self.__updated = True
            self.__sigma_color = int(value)
            print("sigma_color ", self.__sigma_color)
         
    def set_sigma_space(self, value):
        value = int(value)
        if value != self.__sigma_space:
            self.__updated = True
            self.__sigma_space = int(value)
            print("sigma_space ", self.__sigma_space)
        
    def __create_mipmap(self, image):
        pyramid = [image]
        while pyramid[-1].width > 512 and pyramid[-1].height > 512:
            new_img = pyramid[-1].resize(
                (pyramid[-1].width // 2, pyramid[-1].height // 2), Image.NEAREST
            )
            pyramid.append(new_img)
        return pyramid

    def __apply_filter(self):
        # Apply bilateral filter on the numpy array representation of the original image.
        processed_image = cv2.bilateralFilter(np.array(self.__original_image), self.__d, self.__sigma_color, self.__sigma_space)
        #processed_image = cv2.GaussianBlur(np.array(self.__original_image), (self.__d, self.__sigma_color), self.__sigma_space)
        print("applying filter")
        # Convert the processed image back to a PIL Image before creating the mipmap.
        processed_image = Image.fromarray(processed_image)
        self.__image_mipmap = self.__create_mipmap(processed_image)
