from tkinter import Label
from tkinter.font import Font
from typing import Tuple

from hypertext.nodes import Element, Text
from layout.layout_node import LayoutNode
from painting.commands import DrawText
from painting.shapes import Rect

class TextLayoutNode(LayoutNode):

    FONTS = {}

    def __init__(self, node: Element | Text, word: str, parent: LayoutNode, previous: LayoutNode) -> None:
        super().__init__(node, parent, previous)
        self.word = word

    def layout(self) -> None:
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

    def paint(self) -> list:
        color = self.node.style["color"]
        return [DrawText(Rect(self.x, self.y), self.word, self.font, color)]

    def get_font(self, size: int, weight: str, style: str) -> Tuple[Font, Label]:
        key = (size, weight, style)

        if key not in self.FONTS:
            font = Font(size=size, weight=weight, slant=style)
            label = Label(font=font)
            self.FONTS[key] = (font, label)

        return self.FONTS[key][0]
    
    def __repr__(self) -> str:
        return "TextLayoutNode('" + self.word + "', " + (''.join([f"{k}:{v}, " for k, v in self.node.style.items()])[:-2]) + ")"