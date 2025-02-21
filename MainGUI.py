import tkinter as ttk
from tkinter import filedialog
import cv2
from PIL import Image, ImageTk, ImageDraw
import numpy as np
from BlobDetector import BlobDetector
from BlobManager import BlobManager

class MainGUI(ttk.Frame):
    def __init__(self, root):
        self.__create_window(root)
        self.__create_canvas()
        self.__create_menu_bar()
        self.__create_widgets()
        self.__register_actions()


        # Image-related attributes
        self.image = None
        self.ttk_image = None
        self.zoom_factor = 1.0  # Initial zoom factor
        self.original_image = None  # Save original for blob detection
        self.blob_manager = None
        self.blob_detector = None
        self.start_pos = None
        
    def __create_window(self, root):
        title = "Blob Detector"
        ttk.Frame.__init__(self, master=root)
        self.master.title(title)

    def __create_canvas(self):
        # Canvas for displaying the image
        self.canvas = ttk.Canvas(self.master, bg="white")
        self.canvas.pack(fill=ttk.BOTH, expand=True)
        #self.canvas = ttk.Canvas(self.master, width = 200, height = 600, bg="white")
        #self.canvas.pack(pady=15)

        
    def __create_menu_bar(self):
        # Menu bar
        menubar = ttk.Menu(self.master)
        filemenu = ttk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.open_image)
        filemenu.add_command(label="Save", command=self.save_image)
        filemenu.add_command(label="Exit", command=self.master.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        self.master.config(menu=menubar)

    def __create_widgets(self):
        self.min_area_label = ttk.Label(self.master, text="Min Area:")
        self.min_area_label.pack(side=ttk.LEFT)
        self.min_area = ttk.Entry(self.master)
        self.min_area.insert(ttk.END, "100")
        self.min_area.pack(side=ttk.LEFT)

        self.max_area_label = ttk.Label(self.master, text="Max Area:")
        self.max_area_label.pack(side=ttk.LEFT)
        self.max_area = ttk.Entry(self.master)
        self.max_area.insert(ttk.END, "10000")
        self.max_area.pack(side=ttk.LEFT)

        self.detect_button = ttk.Button(self.master, text="Detect Blobs", command=self.detect_blobs)
        self.detect_button.pack(side=ttk.LEFT)

    def __register_actions(self):
        # Bind mouse events for drawing and zooming
        #self.canvas.bind("<ButtonPress-1>", self.start_draw)
        #self.canvas.bind("<B1-Motion>", self.draw_on_image)
        #self.canvas.bind("<MouseWheel>", self.zoom_image)  # Mouse wheel for zooming
        self.canvas.bind("<Button-4>", self.sZoom)     # Linux scroll up
        self.canvas.bind("<Button-5>", self.sZoom)     # Linux scroll down
        
        self.canvas.bind("<B1-Motion>", self.sDrag)
        self.canvas.bind("<ButtonPress-1>", self.sSelection)
        self.canvas.bind("<ButtonRelease-1>", self.resetDragging)

    def sDrag(self, event):
        selected_blob = self.blob_manager.get_selected_blob()
        if(selected_blob is not None):
            #mouse_pos = [event.x, event.y]
            mouse_pos = [self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)]
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
             

        self.display_image()

    def resetDragging(self, event):
        selected_blob = self.blob_manager.get_selected_blob()
        if(selected_blob is not None):
            selected_blob.is_dragging = False
        
    def sSelection(self, event):
        #mouse_pos = [event.x, event.y]
        mouse_pos = [self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)]
        self.blob_manager.set_selected_blob(None)
        thickness = self.blob_manager.get_thickness()

        for blob in self.blob_manager.get_blobs():
            blob_center = [blob.x, blob.y]  
            radius = blob.r  
            
            if( abs(blob_center[0] - mouse_pos[0]) <= radius + thickness and abs(blob_center[1] - mouse_pos[1]) <= radius + thickness and (abs(blob_center[0] - mouse_pos[0]) >= (radius/1.4142) or abs(blob_center[1] - mouse_pos[1]) >= (radius/1.4142))):
                self.blob_manager.set_selected_blob(blob)
                blob.is_dragging = True
                self.start_pos = [event.x, event.y]
                break
            
        self.display_image()
               
    def open_image(self):
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
            self.image = Image.open(file_path)
            self.original_image = np.array(self.image)  # Save original for blob detection

            self.blob_manager = BlobManager()
            self.blob_detector = BlobDetector(self)
            self.zoom_factor = 1.0  # Initial zoom factor
            
            self.draw = ImageDraw.Draw(self.image)
            self.display_image()  # Display the image initially

    def save_image(self):
        if self.image:
            file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                     filetypes=[("PNG Files", "*.png"),
                                                                ("JPEG Files", "*.jpg"),
                                                                ("All Files", "*.*")])
            if file_path:
                self.image.save(file_path)

    def start_draw(self, event):
        self.start_x, self.start_y = event.x, event.y

    def draw_on_image(self, event):
        if self.image:
            self.draw.line([(self.start_x, self.start_y), (event.x, event.y)], fill="red", width=3)
            self.start_x, self.start_y = event.x, event.y  # Update starting position
            self.display_image()

    def detect_blobs(self):
        self.blob_detector.detect_blobs()
        self.display_image()
        
        
    def sZoom(self, event):
        """Handle mouse wheel scrolling."""
        if event.num == 4:  # Linux scroll up
            delta = 1
        elif event.num == 5:  # Linux scroll down
            delta = -1
        else:  # Windows/macOS
            delta = event.delta // 120  # Normalize step size

        self.zoom_factor += (delta/120)

        # Limit the zoom factor to prevent excessive zooming
        self.zoom_factor = max(0.1, min(self.zoom_factor, 10.0))

        # Apply zoom
        self.display_image()

    def draw_blobs(self):
        if self.blob_manager is not None:
            image_with_blobs = self.original_image.copy()
            selected_blob = self.blob_manager.get_selected_blob()
            thickness = self.blob_manager.get_thickness()
        
            for blob in self.blob_manager.get_blobs():
                center = (int(blob.x), int(blob.y))  # Convert to integer for pixel coordinates
                radius = int(blob.r)  # Convert radius to integer
    
                color = (0, 255, 0)  # Color (green in BGR)
                if(selected_blob is not None and blob.id == selected_blob.id):
                    color = (255, 0, 0)
               
                # Draw the circle (blob)
                image_with_blobs = cv2.circle(image_with_blobs, center, radius, color, thickness)
            
            self.image = Image.fromarray(image_with_blobs)
        
    def display_image(self):
        if self.image:
            self.draw_blobs()
            
            # Resize the image based on the zoom factor
            width, height = self.image.size
            new_size = (int(width * self.zoom_factor), int(height * self.zoom_factor))
            
            # Use Image.Resampling.LANCZOS for high-quality resizing
            zoomed_image = self.image.resize(new_size, Image.Resampling.LANCZOS)

            self.ttk_image = ImageTk.PhotoImage(zoomed_image)
            self.canvas.create_image(0, 0, anchor=ttk.NW, image=self.ttk_image)


    def distance(self, p1, p2):
        return np.linalg.norm(np.array(p2) - np.array(p1)) #norm of a vector, means length, not normalize
