import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import math

class PyramidZoomPanCanvas(tk.Canvas):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.image_orig = None      # Full-resolution PIL image.
        self.pyramid = []           # Pyramid of images: level 0 is full-res.
        self.imscale = 1.0          # Overall zoom factor (relative to original).
        self.offset_x = 0           # X offset (canvas coordinate of the image’s top-left).
        self.offset_y = 0           # Y offset.
        self.coord_callback = None  # Function to update the coordinate display.
        self._pan_start = None      # Starting point for panning.

        self.bind("<Button-4>",   self.__on_mousewheel)  # Linux scroll up.
        self.bind("<Button-5>",   self.__on_mousewheel)  # Linux scroll down.
        self.bind("<Button-2>", self.__start_pan)          # Middle-click to start panning.
        self.bind("<B2-Motion>",     self.__do_pan)          # Drag for panning.
        self.bind("<Motion>",        self.__on_mouse_move)   # Update coordinate label.

        parent.bind("<Configure>", self.__on_resize)
        
        
    def load_image(self, image_path):
        """Load the image, build a pyramid, and draw the visible region."""
        self.image_orig = Image.open(image_path)
        self.imscale = 1.0
        self.offset_x = 0
        self.offset_y = 0

        # Build pyramid: level 0 is full res; each subsequent level halves dimensions.
        self.pyramid = [self.image_orig]
        while self.pyramid[-1].width > 512 and self.pyramid[-1].height > 512:
            new_img = self.pyramid[-1].resize(
                (self.pyramid[-1].width // 2, self.pyramid[-1].height // 2),
                Image.NEAREST)
            self.pyramid.append(new_img)
        self.__redraw_image()

    def __redraw_image(self):
        """Redraw the visible region by cropping and scaling the appropriate pyramid level."""
        self.delete("IMG")  # Remove old image                                                                                                                                         
        if self.image_orig is None:
            return

        # Choose pyramid level based on imscale.
        if self.imscale >= 1.0:
            level = 0
        else:
            level = min(-int(math.log(self.imscale, 2)), len(self.pyramid) - 1)
        
        # effective_scale is the scale to apply to the pyramid[level] image
        # so that the displayed image equals original * imscale.
        effective_scale = self.imscale * (2 ** level)
        
        # Determine visible region in canvas coordinates.
        visible_width = self.winfo_width()
        visible_height = self.winfo_height()
        if visible_width < 2 or visible_height < 2:
            self.after(100, self.__redraw_image)
            return

        # Get top-left and bottom-right of the visible canvas in canvas coordinates.
        top_left = [self.canvasx(0), self.canvasy(0)]
        bottom_right = [self.canvasx(visible_width), self.canvasy(visible_height)]
        
        # Convert visible region to original image coordinates.
        orig_x0 = (top_left[0] + self.offset_x) / self.imscale
        orig_y0 = (top_left[1] + self.offset_y) / self.imscale
        orig_x1 = (bottom_right[0] + self.offset_x) / self.imscale
        orig_y1 = (bottom_right[1] + self.offset_y) / self.imscale

        # Convert visible region to pyramid-level coordinates.
        pyr_x0 = orig_x0 / (2 ** level) #is same as orig_x0 * ((1/2) ** level) 
        pyr_y0 = orig_y0 / (2 ** level)
        pyr_x1 = orig_x1 / (2 ** level)
        pyr_y1 = orig_y1 / (2 ** level)

        '''
        If while panning the region goes outside left or top boundary our top left of
        crop region will have a negative number. But we can't crop outside of the image.
        So we crop from 0 and shift the image later in canvas to correct this.

        Optionally we can fill the region outside the image by a white color, but shifting
        in the canvas acheives the same result. It's bit faster too.
        '''
        shift_x = 0
        shift_y = 0
        if pyr_x0 <0:
            shift_x = -self.offset_x
        if pyr_y0 <0:
            shift_y = -self.offset_y
        
        # Clamp coordinates to the pyramid image boundaries.
        pyr_img = self.pyramid[level]
        pyr_x0 = max(pyr_x0, 0)
        pyr_y0 = max(pyr_y0, 0)
        pyr_x1 = min(pyr_x1, pyr_img.width)
        pyr_y1 = min(pyr_y1, pyr_img.height)

        # Calculate new size of the cropped region when scaled.
        new_width = int((pyr_x1 - pyr_x0) * effective_scale)
        new_height = int((pyr_y1 - pyr_y0) * effective_scale)

        if new_width<1 or new_height<1:
            return
        
        # Crop the visible region from the pyramid image.
        region_box = (int(pyr_x0), int(pyr_y0), int(pyr_x1), int(pyr_y1))
        region_img = pyr_img.crop(region_box)

        region_img = region_img.resize((new_width, new_height), Image.NEAREST)

        # Create a PhotoImage from the scaled image.
        self.photo_image = ImageTk.PhotoImage(region_img)

        # Display the image on the canvas.
        self.create_image(shift_x, shift_y, anchor="nw", image=self.photo_image, tag="IMG")


    def __on_mousewheel(self, event):
        """Zoom in/out with the mouse wheel, keeping the point under the mouse fixed."""
        if self.image_orig is None:
            return

        min_scale = 0.025
        max_scale = 16.0

        # Determine zoom factor.
        if event.num == 5 or event.delta == -120:
            if self.imscale <= min_scale:
                scale_factor = 1.0
            else:
                scale_factor = 1 / 2  # zoom out
        elif event.num == 4 or event.delta == 120:
            if self.imscale >= max_scale:
                scale_factor = 1.0
            else:
                scale_factor = 2.0    # zoom in
        else:
            scale_factor = 1.0

        if scale_factor != 1:
            # Get mouse position on canvas.
            x = self.canvasx(event.x)
            y = self.canvasy(event.y)
            # Compute which original image pixel is under the pointer.
            orig_x = (x + self.offset_x) / self.imscale
            orig_y = (y + self.offset_y) / self.imscale

            # Update the overall scale.
            self.imscale *= scale_factor

            # Adjust offset so that (orig_x, orig_y) remains under the mouse.
            self.offset_x =  orig_x * self.imscale - x
            self.offset_y =  orig_y * self.imscale - y

            self.__redraw_image()

    def __start_pan(self, event):
        """Record the starting position for panning."""
        self._pan_start = (event.x, event.y)

    def __do_pan(self, event):
        """Update the offset based on mouse drag and redraw."""
        if self._pan_start is None:
            return

        dx = event.x - self._pan_start[0]
        dy = event.y - self._pan_start[1]
        self._pan_start = (event.x, event.y)
        self.offset_x += -dx
        self.offset_y += -dy
        self.__redraw_image()



    def __on_mouse_move(self, event):
        """Compute and report the original image coordinate under the mouse."""
        if self.image_orig is None:
            return

        x = self.canvasx(event.x)
        y = self.canvasy(event.y)

        orig_x = (x + self.offset_x) / self.imscale
        orig_y = (y + self.offset_y) / self.imscale

        if self.coord_callback:
            self.coord_callback(int(orig_x), int(orig_y))

    def __on_resize(self, event):
        """Redraw the image dynamically when the window is resized."""
        self.after(50, self.__redraw_image) # Delay to avoid excessive redraws

            
def main():
    root = tk.Tk()
    root.title("Pyramid Zoom/Pan")
    
    frame = tk.Frame(root)
    frame.pack(fill="both", expand=True)
    
    #vbar = tk.Scrollbar(frame, orient="vertical")
    #vbar.pack(side="right", fill="y")
    #hbar = tk.Scrollbar(frame, orient="horizontal")
   # hbar.pack(side="bottom", fill="x")
    
    canvas = PyramidZoomPanCanvas(frame, bg="white", width=800, height=600)#,
                                    #xscrollcommand=hbar.set, yscrollcommand=vbar.set)
    canvas.pack(fill="both", expand=True)
    #vbar.config(command=canvas.yview)
    #hbar.config(command=canvas.xview)
    
    coord_label = tk.Label(root, text="Image Coords: (0, 0)")
    coord_label.pack(side="bottom", anchor="w", padx=5, pady=5)
    
    def update_coords(x, y):
        coord_label.config(text=f"Image Coords: ({x}, {y})")
    canvas.coord_callback = update_coords

    def load_image():
        filename = filedialog.askopenfilename(filetypes=[
            ("Image files", ".jpg .jpeg .png .bmp .gif"),
            ("All files", "*.*")
        ])
        if filename:
            canvas.load_image(filename)
    load_btn = tk.Button(root, text="Load Image", command=load_image)
    load_btn.pack(side="top", anchor="w", padx=5, pady=5)
    
    root.mainloop()

if __name__ == "__main__":
    main()
