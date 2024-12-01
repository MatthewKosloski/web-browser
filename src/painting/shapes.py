class Rect:
    def __init__(self, left = 0, top = 0, right = 0, bottom = 0) -> None:
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

    def containsPoint(self, x: int, y: int) -> bool:
        return x >= self.left and x < self.right \
            and y >= self.top and y < self.bottom