class DrawRect:
    def __init__(self, x1, y1, x2, y2, color):
        self.top = y1
        self.left = x1
        self.bottom = y2
        self.right = x2
        self.color = color

    def execute(self, scroll, canvas):
        canvas.create_rectangle(
            self.left,
            self.top - scroll,
            self.right,
            self.bottom - scroll,
            # Do not draw border.
            width=0,
            fill=self.color)
        
    def __repr__(self):
        return f"DrawRect(({self.left}, {self.top}), ({self.right}, {self.bottom}), {self.color})"
        
class DrawText:
    def __init__(self, x1, y1, text, font, color):
        self.top = y1
        self.left = x1
        self.bottom = y1 + font.metrics("linespace")
        self.text = text
        self.font = font
        self.color = color

    def execute(self, scroll, canvas):
        canvas.create_text(
            self.left,
            self.top - scroll,
            text=self.text,
            font=self.font,
            fill=self.color,
            anchor='nw')

    def __repr__(self):
        return f"DrawText(({self.left}, {self.top}), \"{self.text}\", {self.color})"