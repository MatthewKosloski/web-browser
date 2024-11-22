import tkinter
import tkinter.font

from painting.commands import DrawText
from painting.shapes import Rect

class TextLayoutNode:

    FONTS = {}

    def __init__(self, node, word, parent, previous):
        self.node = node
        self.word = word
        self.parent = parent
        self.previous = previous
        self.children = []

    def layout(self):
        weight = self.node.style["font-weight"]
        style = self.node.style["font-style"]

        # Translate CSS "normal" to Tk "roman".
        if style == "normal": style = "roman"

        # Convert CSS pixels to Tk points.
        size = int(float(self.node.style["font-size"][:-2]) * 0.75)

        self.font = self.get_font(size, weight, style)

        self.width = self.font.measure(self.word)

        # If there is a previous sibling, then layout starts right after
        # that sibling. Otherwise, layout starts at the parent's top edge.
        if self.previous:
            space = self.previous.font.measure(" ")
            self.x = self.previous.x + space + self.previous.width
        else:
            self.x = self.parent.x

        self.height = self.font.metrics("linespace")

    def paint(self):
        color = self.node.style["color"]
        return [DrawText(Rect(self.x, self.y), self.word, self.font, color)]

    def get_font(self, size, weight, style):
        key = (size, weight, style)

        if key not in self.FONTS:
            font = tkinter.font.Font(size=size, weight=weight, slant=style)
            label = tkinter.Label(font=font)
            self.FONTS[key] = (font, label)

        return self.FONTS[key][0]
    
    def __repr__(self):
        return "TextLayoutNode('" + self.word + "', " + (''.join([f"{k}:{v}, " for k, v in self.node.style.items()])[:-2]) + ")"