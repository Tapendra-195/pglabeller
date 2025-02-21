class Blob:
    def __init__(self, id, x, y, r, is_dragging = False):#is_selected=False, is_dragging = False):
        self.id = id
        self.x = x
        self.y = y
        self.r = r
        #self.is_selected = is_selected
        self.is_dragging = is_dragging
