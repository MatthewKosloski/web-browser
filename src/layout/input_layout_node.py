from tkinter import Label
from tkinter.font import Font
from typing import Tuple

from constants import INPUT_WIDTH_PX
from hypertext.nodes import HTMLNode, Text
from layout.layout_node import LayoutNode
from painting.commands import DrawText, DrawRect, DrawLine
from painting.shapes import Rect

class InputLayoutNode(LayoutNode):

    FONTS = {}

    def __init__(self, node: HTMLNode, parent: LayoutNode, previous: LayoutNode) -> None:
        super().__init__(node, parent, previous)
        self.width = INPUT_WIDTH_PX

    def layout(self) -> None:
        weight = self.node.style["font-weight"]
        style = self.node.style["font-style"]

        # Translate CSS "normal" to Tk "roman".
        if style == "normal": style = "roman"

        # Translate CSS "900" to Tk "bold".
        if weight == "900": weight = "bold"

        # Convert CSS pixels to Tk points.
        size = int(float(self.node.style["font-size"][:-2]) * 0.75)

        self.font = self.get_font(size, weight, style)

        # If there is a previous sibling, then layout starts right after
        # that sibling. Otherwise, layout starts at the parent's top edge.
        if self.previous:
            space = self.previous.font.measure(" ")
            self.x = self.previous.x + space + self.previous.width
        else:
            self.x = self.parent.x

        self.height = self.font.metrics("linespace")

    def should_paint(self) -> bool:
        return True

    def paint(self) -> list:
        commands = []
        bgcolor = self.node.style.get("background-color", "transparent")

        if bgcolor != "transparent":
            x2, y2 = self.x + self.width, self.y + self.height
            rect = DrawRect(Rect(self.x, self.y, x2, y2), bgcolor)
            commands.append(rect)

        if self.node.tag == "input":
            text = self.node.attributes.get("value", "")
        elif self.node.tag == "button":
            if len(self.node.children) == 1 and \
                isinstance(self.node.children[0], Text):
                    text = self.node.children[0].text
            else:
                print("Ignoring HTML contents inside button")
                text = ""

        if self.node.is_focused:
            cx = self.x + self.font.measure(text)
            commands.append(DrawLine(Rect(cx, self.y, cx, self.y + self.height), "black", 1))

        color = self.node.style["color"]
        commands.append(DrawText(Rect(self.x, self.y), text, self.font, color))

        return commands

    def get_font(self, size: int, weight: str, style: str) -> Tuple[Font, Label]:
        key = (size, weight, style)

        if key not in self.FONTS:
            font = Font(size=size, weight=weight, slant=style)
            label = Label(font=font)
            self.FONTS[key] = (font, label)

        return self.FONTS[key][0]
    
    def __repr__(self) -> str:
        return "InputLayoutNode"