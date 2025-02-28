import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageDraw
import numpy as np
from BlobDetector import BlobDetector
from BlobManager import BlobManager
from PanZoomCanvas import PanZoomCanvas
from LayerRenderer import LayerRenderer
from FilterProcessor import FilterProcessor
from WidgetManager import WidgetManager

#Custom made Widgets
from CustomWidgets.CheckTwoEntryWidget import CheckTwoEntryWidget
from CustomWidgets.LabelTwoSpinboxWidget import LabelTwoSpinboxWidget
from CustomWidgets.LabelSpinboxWidget import LabelSpinboxWidget
from CustomWidgets.LabelEntryWidget import LabelEntryWidget
from CustomWidgets.CheckSpinboxWidget import CheckSpinboxWidget
from CustomWidgets.LabelScaleWidget import LabelScaleWidget

class MainGUI(ttk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)

        self.__create_canvas()
        self.create_styles()  # Create styles for ttk Widgets
        self.__sub_divide_frame() #Divide up frame into canvas, right control and bottom
        
        self.__layer_renderer = LayerRenderer()
        self.__filter_processor = FilterProcessor()
        self.__filter_processor.bind_image(self.__layer_renderer.current_fg)
        
        self.__create_menu_bar()
        self.create_widgets()

        self.__register_actions()

        self.blob_manager = BlobManager()
        self.__blob_detector = BlobDetector()
        self.__blob_detector.bind_blob_manager(self.blob_manager)
        self.__blob_detector.bind_filter_processor(self.__filter_processor)
        self.__use_filter_renderer = False #bool to choose what will be rendered on canvas
        self.__draw_blobs = True
        #self.__current_tool = "draw tool"
        self.__centre = np.array([0,0]) #new blob center
        self.__radius = 0 #new blob radius
        self.__start_drawing = False

        self.__is_image_loaded = False
        self.__select_cursor_tool()
        
    def __create_canvas(self):
        DEFAULT_WIDTH = 800
        DEFAULT_HEIGHT = 600
       
        self.canvas = PanZoomCanvas(self, bg="white")#, width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT)
        #self.canvas = tk.Canvas(self, bg='white', width=300, height=200)
        self.canvas.grid(row=0, column=0, sticky='nsew')

        # Bind rendering system and coordinate callbacks as before
        self.canvas.bind_rendering_system(self.__sRender)
        

        
    def __sub_divide_frame(self):
        # Create the right frame (styled)
        self.right_frame = ttk.Frame(self, width=150)#, style="Right.TFrame")
        self.right_frame.grid(row=0, column=1, sticky='ns')

        # Create the bottom frame (styled)
        self.bottom_frame = ttk.Frame(self, height=50)#, yle="Bottom.TFrame")
        self.bottom_frame.grid(row=1, column=0, columnspan=2, sticky='ew')

        
    def create_styles(self):
        """Define styles for ttk Frames to mimic background colors."""
        style = ttk.Style()
        style.configure("Right.TFrame", background="gray23")  # Right frame style
        style.configure("Bottom.TFrame", background="gray23")  # Bottom frame style
        style.configure("Bold.TLabel", font=("Helvetica", 12, "bold"))
        #style.configure("Custom.TButton", background="black", foreground="white")  # Bottom frame style

        style.configure("Tool.TButton", padding=5)
        # Use style.map to specify background for active and pressed states.
        style.map("Tool.TButton",
                  background=[("active", "lightblue"), ("pressed", "lightblue")])

        # Define a separate style for the selected tool.
        style.configure("Selected.Tool.TButton", padding=5, background="lightblue")
        style.map("Selected.Tool.TButton",
                  background=[("active", "lightblue"), ("pressed", "lightblue")])
        style.map("Selected.Tool.TButton",
          foreground=[('disabled', 'gray')],
          background=[('disabled', 'lightgray')])


        
    def __create_menu_bar(self):
        # Menu bar
        menubar = tk.Menu(self)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.open_image)
        filemenu.add_command(label="Save", command=self.save_image)
        filemenu.add_command(label="Exit", command=self.master.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        self.master.config(menu=menubar)

        
    def create_widgets(self):
        # Create the canvas for the left drawing area
        
        
        # Configure grid weights so the canvas expands but has a minimum size
        self.grid_rowconfigure(0, weight=1, minsize=200)  # Min height 200px
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=1, minsize=300)  # Min width 300px
        self.grid_columnconfigure(1, weight=0)
        
        # Add widgets to the right frame
        #label_right = ttk.Label(self.right_frame, text="Right Label")
        #label_right.pack(pady=10, padx=10)
        #button_right = ttk.Button(self.right_frame, text="Right Button")
        #button_right.pack(pady=10, padx=10)

        # Create WidgetManager for the right controls.
        self.__right_widget_manager = WidgetManager(self.right_frame)
        
        self.__right_widget_manager.add_widget("load_background", ttk.Button, text="Load Background", command=self.__load_background)
        self.__right_widget_manager.add_widget("change_opacity", LabelScaleWidget, label_text = "Fg Opacity", min_value=0, max_value=1, default_value = 1.0, command=self.__on_opacity_change)
        
        #Blob parameters
        self.__right_widget_manager.add_widget("blob_parameters", ttk.Label, text="Blob Parameters", style = "Bold.TLabel")
        
        self.__right_widget_manager.add_widget("Color", CheckSpinboxWidget, label_text="Color", default_values=(True,255), min_value=0, max_value=255)
        self.__right_widget_manager.add_widget("Area", CheckTwoEntryWidget, label_text="Area", default_values=(True, 100, 1000), min_value = 1, max_value = 100000000000000)
        self.__right_widget_manager.add_widget("Inertia", CheckTwoEntryWidget, label_text="Inertia", default_values=(True, 0.001, 1), min_value = 0.001, max_value = 1.0)
        self.__right_widget_manager.add_widget("Circularity", CheckTwoEntryWidget, label_text="Circularity", default_values=(True, 0.001, 1), min_value = 0.001, max_value = 1.0)
        self.__right_widget_manager.add_widget("Convexity", CheckTwoEntryWidget, label_text="Convexity", default_values=(True, 0.001, 1), min_value = 0.001, max_value = 1.0)
        self.__right_widget_manager.add_widget("Threshold", LabelTwoSpinboxWidget, label_text="Threshold", default_values=(0, 255), min_value = 0, max_value = 255)
        self.__right_widget_manager.add_widget("Blob_Min_Dist", LabelEntryWidget, label_text="Min Dist betn Blobs", default_value=1, min_value = 1)

        self.__right_widget_manager.add_widget("total_blobs", ttk.Label, text="Total Blobs: 0", style = "Bold.TLabel")
        self.__right_widget_manager.add_widget("detect_blobs", ttk.Button, text="Detect Blobs", command=self.detect_blobs)
        
        #Filter options
        self.__right_widget_manager.add_widget("filter_parameters", ttk.Label, text="Filter Parameters", style = "Bold.TLabel")
        self.__right_widget_manager.add_widget("show_filtered", ttk.Checkbutton, text="Show Filtered Image", command=self.__toggle_renderer)
        self.__right_widget_manager.add_widget("d", LabelSpinboxWidget, label_text="d", default_value=5, min_value = 0, max_value = 10)
        self.__right_widget_manager.add_widget("sigma_color", LabelSpinboxWidget, label_text="Sigma Color", default_value=75, min_value = 0, max_value = 255)
        self.__right_widget_manager.add_widget("sigma_space", LabelEntryWidget, label_text="Sigma Space", default_value=75, min_value = 0)
        #Min dist betn blobs -
        #Threshold - -
 
        

        

        
        
        
        # --- Bottom Frame (Status/Extra Controls) ---
        # Create the bottom frame as a child of the container so it spans full width.
        #self.__bottom_frame = ttk.Frame(self.container, padding="5", relief="raised", borderwidth=2)
        #self.__bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.__bottom_widget_manager = WidgetManager(self.bottom_frame)
        self.__bottom_widget_manager.add_widget("coord", ttk.Label, text="", layout_options={'side': 'left', 'padx': 10})
        self.__bottom_widget_manager.add_widget("scale", ttk.Label, text="", layout_options={'side': 'left', 'padx': 10})
        #self.__bottom_widget_manager.add_widget("edit_mode", ttk.Button, text="Edit Mode", layout_options={'side': 'left', 'padx': 10}, command=self.__change_to_edit_mode)
        #self.__bottom_widget_manager.add_widget("label_mode", ttk.Button, text="Label Mode", layout_options={'side': 'left', 'padx': 10}, command=self.__change_to_label_mode)

        self.__bottom_widget_manager.add_widget("cursor", ttk.Button, text="Cursor", layout_options={'side': 'left', 'padx': 10}, style="Tool.TButton", command=self.__select_cursor_tool)
        self.__bottom_widget_manager.add_widget("draw_circle", ttk.Button, text="Draw Circle", layout_options={'side': 'left', 'padx': 10}, style="Tool.TButton", command=self.__select_circle_tool)
        
        self.__bottom_widget_manager.add_widget("show_blobs", ttk.Checkbutton, text="Show Blobs", layout_options={'side': 'left', 'padx': 10}, variable=tk.IntVar(value=1), command=self.__show_blobs)
        
        
        
        '''
        # Add widgets to the bottom frame
        label_bottom = ttk.Label(self.bottom_frame, text="Bottom Label")
        label_bottom.pack(side='left', padx=10, pady=10)
        button_bottom = ttk.Button(self.bottom_frame, text="Bottom Button")
        button_bottom.pack(side='left', padx=10, pady=10)
        '''


    def __set_drawing(self, cx, cy):
        if not self.__is_image_loaded:
            return

        if self.__current_tool == "cursor tool":
            return
        
        if self.__current_tool == "draw tool":
            self.__start_drawing = not self.__start_drawing
            if self.__start_drawing:
                self.__centre = self.canvas.screen_to_orig_image_coord(np.array([cx, cy]))
                self.__radius = 0
            else:
                if self.__radius > 0:
                    self.blob_manager.add_blob(self.__centre[0], self.__centre[1], self.__radius)
                    self.__radius = 0
                    self.canvas.redraw()
        else:
            print("Error Unknown Tool selected")
                
    def __register_actions(self):
        self.canvas.register_left_button_click(self.__sSelection)
        self.canvas.register_left_button_release(self.__set_drawing)
        self.canvas.register_left_button_drag(self.__sDrag)
        self.canvas.register_right_button_click(self.__reset_drawing)
        self.canvas.register_del_key(self.__delete_selected_blob)
        self.canvas.register_mouse_move(self.__handle_mouse_movement)

    def __draw_new_blob(self):
        self.canvas.delete("newBlobLayer")
        
        if not self.__is_image_loaded:
            return
        
        if self.__radius == 0:
            return
                
        thickness = self.blob_manager.get_thickness()
        p0 = np.array([self.__centre[0] - self.__radius, self.__centre[1] - self.__radius])
        p1 = np.array([self.__centre[0] + self.__radius, self.__centre[1] + self.__radius])
        color = "yellow"#(0, 255, 0)  # Color (green in BGR)
        
        x0, y0 = self.canvas.orig_image_to_screen(p0)
        x1, y1 = self.canvas.orig_image_to_screen(p1)
        
        self.canvas.create_oval(x0, y0, x1, y1, outline=color, width=thickness, tag="newBlobLayer")

        
    def __handle_mouse_movement(self, cx, cy):
        if not self.__is_image_loaded:
            return
        
        
        orig_coord = self.canvas.screen_to_orig_image_coord(np.array([cx, cy])) #Current pos of cursor
        if self.__start_drawing:
            self.__radius = self.__distance(self.__centre, orig_coord)
            self.__draw_new_blob()
            
                
        self.__update_coords(int(orig_coord[0]), int(orig_coord[1]))
        
    def __delete_selected_blob(self,event):
        if self.__current_tool == "draw tool":
            return
        
        self.blob_manager.delete_selected_blob()
        self.canvas.redraw()
        
    def __sDrag(self, cx, cy):
        if not self.__is_image_loaded:
            return
        
        if self.__current_tool == "draw tool":
            return
        
        
        selected_blob = self.blob_manager.get_selected_blob()
        if(selected_blob is not None):
            #mouse_pos = [event.x, event.y]
            mouse_pos = self.canvas.screen_to_orig_image_coord(np.array([cx, cy]))
            del_pos = [mouse_pos[0] - self.start_pos[0], mouse_pos[1] - self.start_pos[1]]
            thickness = self.blob_manager.get_thickness()
            blob_center = [selected_blob.x, selected_blob.y] 
            radius = selected_blob.r  
            
            if(selected_blob.is_dragging):
                selected_blob.x += del_pos[0]
                selected_blob.y += del_pos[1]

                self.start_pos = mouse_pos
  
            else:
                if( abs(blob_center[0] - mouse_pos[0]) <= radius + thickness and abs(blob_center[1] - mouse_pos[1]) <= radius + thickness and (abs(blob_center[0] - mouse_pos[0]) >= (radius/1.4142) or abs(blob_center[1] - mouse_pos[1]) >= (radius/1.4142))):
                    selected_blob.is_dragging = True
             

        self.canvas.redraw()

    def __reset_drawing(self, cx, cy):
        if self.__current_tool == "cursor tool":
            return

        if self.__start_drawing:
            self.canvas.delete("newBlobLayer")
            self.__radius = 0
            self.__start_drawing = False
        #if(selected_blob is not None):
        #    selected_blob.is_dragging = False
        
    def __sSelection(self, cx, cy):
        if self.__current_tool == "draw tool":
            return
        
        #mouse_pos = [event.x, event.y]
        mouse_pos = self.canvas.screen_to_orig_image_coord(np.array([cx, cy]))
        #mouse_pos = [self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)]
        self.blob_manager.set_selected_blob(None)
        thickness = self.blob_manager.get_thickness()

        for blob in self.blob_manager.get_blobs():
            blob_center = [blob.x, blob.y]  
            radius = blob.r  
            
            if( abs(blob_center[0] - mouse_pos[0]) <= radius + thickness and abs(blob_center[1] - mouse_pos[1]) <= radius + thickness and (abs(blob_center[0] - mouse_pos[0]) >= (radius/1.4142) or abs(blob_center[1] - mouse_pos[1]) >= (radius/1.4142))):
                self.blob_manager.set_selected_blob(blob)
                blob.is_dragging = True
                self.start_pos = mouse_pos
                break
            
        self.canvas.redraw()
               
        
               
    def open_image(self):
        filename = filedialog.askopenfilename(
            filetypes=[("Image files", ".jpg .jpeg .png .bmp .gif"), ("All files", "*.*")]
        )
        if filename:
            self.__layer_renderer.load_foreground(filename)
            #self.__filter_processor.reload_image()
            self.__filter_processor.bind_image(self.__layer_renderer.current_fg)
            
            self.blob_manager.reset()
            self.__is_image_loaded = True
            self.canvas.reset()
        '''
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Image Files", ".png .jpg .jpeg .bmp .JPG .JPEG .BMP"),
                ("PNG", ".png"),
                ("JPG", ".jpg .JPG .jpeg .JPEG"),
                ("BMP", ".bmp .BMP"),
                ("All Files", "*.*")
            ]
        )
        if file_path:
            self.canvas.load_image(file_path)
            #self.image = Image.open(file_path)
            #self.original_image = np.array(self.image)  # Save original for blob detection

            self.blob_manager = BlobManager()
            self.blob_detector = BlobDetector(self)
            self.zoom_factor = 1.0  # Initial zoom factor
            
            self.draw = ImageDraw.Draw(self.canvas.pyramid[0])
            #self.display_image()  # Display the image initially
        '''
        
    def save_image(self):
        if not self.__is_image_loaded:
            return

        
        if self.image:
            file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                     filetypes=[("PNG Files", "*.png"),
                                                                ("JPEG Files", "*.jpg"),
                                                                ("All Files", "*.*")])
            if file_path:
                self.image.save(file_path)


    def __sRender(self, orig_top_left, orig_bottom_right, scale):
        if not self.__is_image_loaded:
            return

        self.canvas.delete("IMG")
        self.canvas.delete("BlobLayer")
        
        scale_label = str(scale) + " X"
        self.__bottom_widget_manager.get_widget("scale").config(text=scale_label)
        
        
        if self.__use_filter_renderer:
            self.__filter_processor.render(orig_top_left, orig_bottom_right, scale)
            current_render, shift = self.__filter_processor.get_render()
        else:
            self.__layer_renderer.render(orig_top_left, orig_bottom_right, scale)   
            current_render, shift = self.__layer_renderer.get_render()
            
        if current_render is None:
            return
        
        
        self.canvas.create_image( shift[0], shift[1], anchor="nw", image=current_render, tag="IMG" )

        #self.canvas.delete("BlobLayer")
        if not self.__use_filter_renderer:
            self.__render_blobs(scale)

        self.__draw_new_blob()


    def __render_blobs(self, scale):
        
        text = "Total Blobs: " + str(len(self.blob_manager.get_blobs()))
        self.__right_widget_manager.get_widget("total_blobs").config(text=text)
           
        if not self.__draw_blobs:
            return
        
        if self.blob_manager is not None:
            #image_with_blobs = self.original_image.copy()
            selected_blob = self.blob_manager.get_selected_blob()
            thickness = self.blob_manager.get_thickness()
            #print("total blobs found = " ,len(self.blob_manager.get_blobs()))
            for blob in self.blob_manager.get_blobs():
                center = (int(blob.x), int(blob.y))  # Convert to integer for pixel coordinates
                radius = int(blob.r)  # Convert radius to integer
                
                color = "green"#(0, 255, 0)  # Color (green in BGR)
                if(selected_blob is not None and blob.id == selected_blob.id):
                    color = "red"#(255, 0, 0)

                center = self.canvas.orig_image_to_screen(np.array(center))
                radius = radius*scale
                #thickness /= scale
                x0, y0 = center[0] - radius, center[1] - radius
                x1, y1 = center[0] + radius, center[1] + radius
                    
                
                #self.canvas.create_oval( shift[0], shift[1], anchor="nw", image=current_render, tag="BlobLayer" )
                self.canvas.create_oval(x0, y0, x1, y1, outline=color, width=thickness, tag="BlobLayer")

                #self.canvas.focus_set()

                # Draw the circle (blob)
                #image_with_blobs = cv2.circle(image_with_blobs, center, radius, color, thickness)
            #self.image = Image.fromarray(image_with_blobs)
            
    def __set_blob_detector_params(self):
        filter_by_color, color = self.__right_widget_manager.get_widget("Color").get_values() 
        filter_by_area, min_area, max_area = self.__right_widget_manager.get_widget("Area").get_values()
        filter_by_inertia, min_inertia, max_inertia = self.__right_widget_manager.get_widget("Inertia").get_values()
        filter_by_circularity, min_circularity, max_circularity = self.__right_widget_manager.get_widget("Circularity").get_values()
        filter_by_convexity, min_convexity, max_convexity = self.__right_widget_manager.get_widget("Convexity").get_values()
        min_threshold, max_threshold = self.__right_widget_manager.get_widget("Threshold").get_values()
        min_dist_between_blobs = self.__right_widget_manager.get_widget("Blob_Min_Dist").get_value()

        color = int(color.strip())
        min_area = int(min_area.strip())
        max_area = int(max_area.strip())
        min_inertia = float(min_inertia.strip())
        max_inertia = float(max_inertia.strip())
        min_circularity = float(min_circularity.strip())
        max_circularity = float(max_circularity.strip())
        min_convexity = float(min_convexity.strip())
        max_convexity = float(max_convexity.strip())
        min_threshold = int(min_threshold.strip())
        max_threshold = int(max_threshold.strip())
        min_dist_between_blobs = int(min_dist_between_blobs.strip())
        
        #Set the params
        self.__blob_detector.set_color_params(filter_by_color, color)
        self.__blob_detector.set_area_params(filter_by_area, min_area, max_area)        
        self.__blob_detector.set_inertia_params(filter_by_inertia, min_inertia, max_inertia)
        self.__blob_detector.set_circularity_params(filter_by_circularity, min_circularity, max_circularity)
        self.__blob_detector.set_convexity_params(filter_by_convexity, min_convexity, max_convexity)
        self.__blob_detector.set_threshold_params(min_threshold, max_threshold)
        self.__blob_detector.set_min_distance_param(min_dist_between_blobs)

    def __set_filter_params(self):
        d = self.__right_widget_manager.get_widget("d").get_value()
        sigma_color = self.__right_widget_manager.get_widget("sigma_color").get_value()
        sigma_space = self.__right_widget_manager.get_widget("sigma_space").get_value()

        self.__filter_processor.set_d(d)
        self.__filter_processor.set_sigma_color(sigma_color)
        self.__filter_processor.set_sigma_space(sigma_space)

            
    def detect_blobs(self):
        if not self.__is_image_loaded:
            return

        self.__right_widget_manager.disable_widget("detect_blobs")
        self.__set_filter_params()
        self.__set_blob_detector_params()
        
        
        #print(self.__right_widget_manager.get_widget("Area").get_values())
        
        #min_area = int(self.min_area.get() if hasattr(self.min_area, 'get') else 10)
        #max_area = int(self.max_area.get() if hasattr(self.max_area, 'get') else 1000)
        
        self.__blob_detector.detect_blobs()
        self.canvas.redraw()
        self.__right_widget_manager.enable_widget("detect_blobs")
        #self.display_image()


    def __load_background(self):
        if not self.__is_image_loaded:
            return

        filename = filedialog.askopenfilename(
            filetypes=[("Image files", ".jpg .jpeg .png .bmp .gif"), ("All files", "*.*")]
        )
        if filename:
            self.__layer_renderer.load_background(filename)
            self.canvas.redraw()

    def __on_opacity_change(self, val):
        self.__layer_renderer.set_opacity(float(val))
        self.canvas.redraw()


    def __toggle_renderer(self):
        if not self.__is_image_loaded:
            return

        self.__use_filter_renderer = not self.__use_filter_renderer 
        
        self.__set_filter_params()
        
        if self.__use_filter_renderer:
            self.__right_widget_manager.disable_widget("d")
            self.__right_widget_manager.disable_widget("sigma_color")
            self.__right_widget_manager.disable_widget("sigma_space")
            self.__right_widget_manager.disable_widget("change_opacity")
            self.__right_widget_manager.disable_widget("cursor")
            self.__right_widget_manager.disable_widget("draw_circle")
        else:
            self.__right_widget_manager.enable_widget("d")
            self.__right_widget_manager.enable_widget("sigma_color")
            self.__right_widget_manager.enable_widget("sigma_space")
            self.__right_widget_manager.enable_widget("change_opacity")
            self.__right_widget_manager.enable_widget("cursor")
            self.__right_widget_manager.enable_widget("draw_circle")
       
            
        self.canvas.redraw()

    def __update_coords(self, x, y):
        coord = "( " + str(x) + " , " + str(y) + " )"
        self.__bottom_widget_manager.get_widget("coord").config(text=coord)


    def __change_to_edit_mode(self):
        print("Edit Mode")

    def __change_to_label_mode(self):
        print("Label Mode")

    def __show_blobs(self):
        self.__draw_blobs = not self.__draw_blobs
        self.canvas.redraw()

    def __distance(self, p1, p2):
        return np.linalg.norm(np.array(p2) - np.array(p1)) #norm of a vector, means length, not normalize

    def __select_cursor_tool(self):
        self.__current_tool = "cursor tool"
        self.__bottom_widget_manager.get_widget("cursor").config(style="Selected.Tool.TButton")
        self.__bottom_widget_manager.get_widget("draw_circle").config(style="Tool.TButton")

    def __select_circle_tool(self):
        self.__current_tool = "draw tool"
        
        self.__bottom_widget_manager.get_widget("cursor").config(style="Tool.TButton")
        self.__bottom_widget_manager.get_widget("draw_circle").config(style="Selected.Tool.TButton")
        
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Custom Frame Example")
    root.geometry("800x600")  # Set initial window size
    
    # Prevent the window from shrinking below a certain size
    root.minsize(800, 700)  # Minimum window size
    
    # Create and pack our custom frame
    main_gui = MainGUI(root)
    main_gui.pack(fill="both", expand=True)
    
    root.mainloop()
