
class Rect:
    def __init__(self, x, y, width, height):
        self.x1 = x
        self.y1 = y
        self.x2 = x + width
        self.y2 = y + height

    def get_center_coords(self):
        center_x = (self.x1 + self.x2) // 2
        center_y = (self.y1 + self.y2) // 2
        return center_x, center_y

    def is_intersecting(self, other_rect):
        # returns true if this rectangle intersects other rectangle
        return (self.x1 <= other_rect.x2 and self.x2 >= other_rect.x1 and
                self.y1 <= other_rect.y2 and self.y2 >= other_rect.y1)
