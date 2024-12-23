from __future__ import annotations

from typing import Tuple
from tkinter import Label
from tkinter.font import Font

from constants import VERTICAL_STEP, INPUT_WIDTH_PX
from hypertext.nodes import Element, Text, HTMLNode
from layout.input_layout_node import InputLayoutNode
from layout.layout_node import LayoutNode
from layout.line_layout_node import LineLayoutNode
from layout.text_layout_node import TextLayoutNode
from painting.commands import DrawRect
from painting.shapes import Rect

class BlockLayoutNode(LayoutNode):

    LEADING = 1.25
    FONTS = {}
    BLOCK_ELEMENTS = [
        "html", "body", "article", "section", "nav", "aside",
        "h1", "h2", "h3", "h4", "h5", "h6", "hgroup", "header",
        "footer", "address", "p", "hr", "pre", "blockquote",
        "ol", "ul", "menu", "li", "dl", "dt", "dd", "figure",
        "figcaption", "main", "div", "table", "form", "fieldset",
        "legend", "details", "summary"
    ]

    def __init__(self, node: HTMLNode, parent: LayoutNode, previous: LayoutNode) -> None:
        super().__init__(node, parent, previous)

    def should_paint(self) -> bool:
        return isinstance(self.node, Text) \
            or (self.node.tag != "input" and self.node.tag != "button")

    def paint(self) -> list:
        commands = []

        if isinstance(self.node, Element) and self.node.tag == "pre":

            bgcolor = self.node.style.get("background-color", "transparent")

            if bgcolor != "transparent":
                x2, y2 = self.x + self.width, self.y + self.height
                rect = DrawRect(Rect(self.x, self.y, x2, y2), bgcolor)
                commands.append(rect)

        return commands

    def layout(self) -> None:
        # To compute a block's x position, the x position of its parent block
        # must already have been computed. So a block's x must therefore be
        # computed before its children's x.
        self.x = self.parent.x

        # If there is a previous sibling, then layout starts right after
        # that sibling. Otherwise, layout starts at the parent's top edge.
        if self.previous:
            self.y = self.previous.y + self.previous.height
        else:
            self.y = self.parent.y


        mode = self.layout_mode()
        self.width = self.parent.width

        if mode == "block":
            previous = None
            for child in self.node.children:
                # Exclude these tags from the layout tree.
                if isinstance(child, Element) and child.tag not in ['head', 'script']:
                    next = BlockLayoutNode(child, self, previous)
                    self.children.append(next)
                    previous = next
        else:
            self.cursor_x = 0
            self.cursor_y = 0
            self.weight = "normal"
            self.style = "roman"
            self.size = 12

            self.new_line()
            self.recurse(self.node)

            # We need to be tall enough to contain the text.
            self.height = self.cursor_y

        for child in self.children:
            child.layout()

        # Height is the sum of all the children's heights. Therefore,
        # we need to compute the height after laying out the children.
        self.height = sum([child.height for child in self.children])

    def layout_mode(self) -> str:
        if isinstance(self.node, Text):
            return "inline"
        elif any([isinstance(child, Element) and \
                child.tag in self.BLOCK_ELEMENTS
                for child in self.node.children]):
            # There is at least one child that is a block element.
            return "block"
        elif self.node.children:
            # There are zero children that are block elements.
            return "inline"
        elif self.node.tag == "input":
            # Inputs don't have children, but they should have inline layout.
            return "inline"
        else:
            # The node doesn't have any children; assume block element.
            return "block"

    def recurse(self, node: HTMLNode) -> None:
        if isinstance(node, Element) and node.tag in self.BLOCK_ELEMENTS:
            # Add a gap between paragraphs.
            self.cursor_y += VERTICAL_STEP

        if isinstance(node, Text):
            for word in node.text.split():
                self.word(node, word)
        else:
            if node.tag == "br":
                self.new_line()
            elif node.tag == "input" or node.tag == "button":
                self.input(node)
            else:
                for child in node.children:
                    self.recurse(child)

    def word(self, node: Text, word: str) -> None:
        weight = node.style["font-weight"]
        style = node.style["font-style"]

        # Translate CSS "normal" to Tk "roman".
        if style == "normal": style = "roman"

        # Translate CSS "900" to Tk "bold".
        if weight == "900": weight = "bold"

        # Convert CSS pixels to Tk points.
        size = int(float(node.style["font-size"][:-2]) * 0.75)

        font = self.get_font(size, weight, style)
        w = font.measure(word)

        if self.cursor_x + w > self.width:
            # Wrap text to next line.
            self.new_line()
        
        line = self.children[-1]
        previous_word = line.children[-1] if line.children else None
        text = TextLayoutNode(node, word, line, previous_word)
        line.children.append(text)

        # " " adds back the whitespace that was removed when splitting the text.
        self.cursor_x += w + font.measure(" ")

    def input(self, node: Text) -> None:
        w = INPUT_WIDTH_PX

        weight = node.style["font-weight"]
        style = node.style["font-style"]

        # Translate CSS "normal" to Tk "roman".
        if style == "normal": style = "roman"

        # Translate CSS "900" to Tk "bold".
        if weight == "900": weight = "bold"

        # Convert CSS pixels to Tk points.
        size = int(float(node.style["font-size"][:-2]) * 0.75)

        font = self.get_font(size, weight, style)

        if self.cursor_x + w > self.width:
            # Wrap text to next line.
            self.new_line()
        
        line = self.children[-1]
        previous_word = line.children[-1] if line.children else None
        input = InputLayoutNode(node, line, previous_word)
        line.children.append(input)

        # " " adds back the whitespace that was removed when splitting the text.
        self.cursor_x += w + font.measure(" ")

    def new_line(self) -> None:
        self.cursor_x = 0
        last_line = self.children[-1] if self.children else None
        new_line = LineLayoutNode(self.node, self, last_line)
        self.children.append(new_line)

    def get_font(self, size: int, weight: str, style: str) -> Tuple[Font, Label]:
        key = (size, weight, style)

        if key not in self.FONTS:
            font = Font(size=size, weight=weight, slant=style)
            label = Label(font=font)
            self.FONTS[key] = (font, label)

        return self.FONTS[key][0]
    
    def __repr__(self) -> str:
        return "BlockLayoutNode('" + self.node.tag + "', " + (''.join([f"{k}:{v}, " for k, v in self.node.style.items()])[:-2]) + ")"
    
