import cv2
import numpy as np
from PIL import Image
from typing import TYPE_CHECKING
from Blob import Blob
from BlobManager import BlobManager


class BlobDetector:
    def __init__(self):
        """
        Initialize the BlobDetector with a reference to the MainGUI instance.
        :param main_gui: The instance of MainGUI.
        """
        #self.main_gui = main_gui
        #self.gray_image = None
        self.__blob_manager = None
        self.__filter_processor = None
        self.__params = cv2.SimpleBlobDetector_Params()
        
    def bind_blob_manager(self, blob_manager):
        self.__blob_manager = blob_manager

    def bind_filter_processor(self, filter_processor):
        self.__filter_processor = filter_processor
    
        
    def detect_blobs(self):
        if self.__filter_processor is None:
            print("Bind filter processor before blob detection")
            return

        if self.__blob_manager is None:
            print("Bind blob manager before blob detection")
            return

        
        #Delete previously detected blobs
        self.__blob_manager.reset()
        #get the filtered image
        gray_image = self.__filter_processor.get_current_image()
            
        if gray_image is not None:
            # Blob detector parameters
            #min_area = 10#int(self.main_gui.min_area.get() if hasattr(self.main_gui.min_area, 'get') else self.main_gui.min_area)
            #max_area = 10000#int(self.main_gui.max_area.get() if hasattr(self.main_gui.max_area, 'get') else self.main_gui.max_area)

            detector = cv2.SimpleBlobDetector_create(self.__params)

            # Detect blobs
            keypoints = detector.detect(gray_image)

            for keypoint in keypoints:
                x, y = keypoint.pt  # Extract x, y from the keypoint
                r = keypoint.size / 2  # Extract radius (half the size)
    
                # Create a Blob and add it to the BlobManager
                self.__blob_manager.add_blob(x, y, r)


    def set_color_params(self, filter_by_color, color):
        self.__params.filterByColor = filter_by_color
        self.__params.blobColor = color
       
            
    def set_area_params(self, filter_by_area, minArea, maxArea):
        self.__params.filterByArea = filter_by_area
        self.__params.minArea = minArea
        self.__params.maxArea = maxArea

    def set_inertia_params(self, filter_by_inertia, minInertia, maxInertia):
        self.__params.filterByArea = filter_by_inertia
        self.__params.minInertiaRatio = minInertia
        self.__params.maxInertiaRatio = maxInertia


    def set_circularity_params(self, filter_by_circularity, minCircularity, maxCircularity):
        print("circularity ", minCircularity, " , " ,maxCircularity)
        self.__params.filterByCircularity = filter_by_circularity
        self.__params.minCircularity = minCircularity
        self.__params.maxCircularity = maxCircularity

    def set_convexity_params(self, filter_by_convexity, minConvexity, maxConvexity):
        self.__params.filterByConvexity = filter_by_convexity
        self.__params.minConvexity = minConvexity
        self.__params.maxConvexity = maxConvexity

    def set_threshold_params(self, minThreshold, maxThreshold):
        self.__params.minThreshold = minThreshold
        self.__params.maxThreshold = maxThreshold

    def set_min_distance_param(self, minDist):
        self.__params.minDistBetweenBlobs = minDist
