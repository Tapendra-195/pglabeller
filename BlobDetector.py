import cv2
import numpy as np
from PIL import Image
from typing import TYPE_CHECKING
from Blob import Blob
from BlobManager import BlobManager

if TYPE_CHECKING:
    from MainGUI import MainGUI  # Only imported for type hints (avoids circular import)

class BlobDetector:
    def __init__(self, main_gui):
        """
        Initialize the BlobDetector with a reference to the MainGUI instance.
        :param main_gui: The instance of MainGUI.
        """
        self.main_gui = main_gui
        self.gray_image = None

    def detect_blobs(self):
        """Detect and highlight blobs in the image."""
        self.main_gui.blob_manager = BlobManager()
        if self.main_gui.original_image is not None and self.gray_image is None:
            self.gray_image = cv2.cvtColor(self.main_gui.original_image, cv2.COLOR_RGB2GRAY)
            
        if self.gray_image is not None:
            # Blob detector parameters
            min_area = int(self.main_gui.min_area.get() if hasattr(self.main_gui.min_area, 'get') else self.main_gui.min_area)
            max_area = int(self.main_gui.max_area.get() if hasattr(self.main_gui.max_area, 'get') else self.main_gui.max_area)

            params = cv2.SimpleBlobDetector_Params()
            params.filterByArea = True
            params.minArea = min_area
            params.maxArea = max_area

            detector = cv2.SimpleBlobDetector_create(params)

            # Detect blobs
            keypoints = detector.detect(self.gray_image)

            for keypoint in keypoints:
                x, y = keypoint.pt  # Extract x, y from the keypoint
                r = keypoint.size / 2  # Extract radius (half the size)
    
                # Create a Blob and add it to the BlobManager
                self.main_gui.blob_manager.add_blob(x, y, r)
