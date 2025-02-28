from Blob import Blob

class BlobManager:
    def __init__(self):
        self.blobs = []
        self.selected_blob = None
        self.total_blobs = 0
        self.thickness = 5
        
    def add_blob(self, x, y, r):
        """Add a blob to the array."""
        self.blobs.append(Blob(self.total_blobs, x, y, r))
        self.total_blobs += 1
        
    def get_blobs(self):
        """Return the list of all blobs."""
        return self.blobs

    def get_selected_blob(self):
        """Return the list of all blobs."""
        return self.selected_blob

    def set_selected_blob(self, blob):
        """Return the list of all blobs."""
        self.selected_blob = blob

    def set_thickness(self, thickness):
        self.thickness = thickness

    def get_thickness(self):
        return self.thickness

    def reset(self):
        self.blobs = []
        self.selected_blob = None
        self.total_blobs = 0


    def delete_selected_blob(self):
        """Delete the currently selected blob from the blobs list."""
        if self.selected_blob is not None:
            try:
                self.blobs.remove(self.selected_blob)
                self.selected_blob = None
            except ValueError:
                print("Selected blob not found in the blobs list.")
            self.selected_blob = None
        else:
            print("No blob is currently selected.")
