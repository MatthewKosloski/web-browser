class DrawText:
    def __init__(self, x1, y1, text, font):
        self.top = y1
        self.left = x1
        self.bottom = y1 + font.metrics("linespace")
        self.text = text
        self.font = font

    def execute(self, scroll, canvas):
        canvas.create_text(
            self.left,
            self.top - scroll,
            text=self.text,
            font=self.font,
            anchor='nw')