import tkinter
import tkinter.font

from constants import HORIZONTAL_STEP, VERTICAL_STEP
from hypertext.nodes import Element, Text
from painting.commands import DrawRect, DrawText

class BlockLayoutNode:

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

    def __init__(self, node, parent, previous):
        self.node = node
        self.parent = parent
        self.previous = previous
        self.children = []
        self.x = None
        self.y = None
        self.width = None
        self.height = None
        self.display_list = []

    def paint(self):
        commands = []

        if isinstance(self.node, Element) and self.node.tag == "pre":

            bgcolor = self.node.style.get("background-color", "transparent")

            if bgcolor != "transparent":
                x2, y2 = self.x + self.width, self.y + self.height
                rect = DrawRect(self.x, self.y, x2, y2, bgcolor)
                commands.append(rect)

        if self.layout_mode() == "inline":
            for x, y, word, font in self.display_list:
                commands.append(DrawText(x, y, word, font))
        return commands

    def layout(self):
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
                if child.tag not in ['head', 'script']:
                    next = BlockLayoutNode(child, self, previous)
                    self.children.append(next)
                    previous = next
        else:
            self.cursor_x = 0
            self.cursor_y = 0
            self.weight = "normal"
            self.style = "roman"
            self.size = 12

            self.line = []
            self.recurse(self.node)

            # We need to be tall enough to contain the text.
            self.height = self.cursor_y

            self.flush()

        for child in self.children:
            child.layout()

        if mode == "block":
            # Height is the sum of all the children's heights. Therefore,
            # we need to compute the height after laying out the children.
            self.height = sum([child.height for child in self.children])

    def layout_mode(self):
        if isinstance(self.node, Text):
            return "inline"
        elif any([isinstance(child, Element) and \
                child.tag in self.BLOCK_ELEMENTS
                for child in self.node.children]):
            return "block"
        elif self.node.children:
            return "inline"
        else:
            return "block"

    def recurse(self, tree):
        if isinstance(tree, Text):
            for word in tree.text.split():
                self.word(word)
        else:
            self.open_tag(tree.tag)
            for child in tree.children:
                self.recurse(child)
            self.close_tag(tree.tag)

    def open_tag(self, tag):
        if tag == "i":
            self.style = "italic"
        elif tag == "b":
            self.weight = "bold"
        elif tag == "small":
            self.size -= 2
        elif tag == "big":
            self.size += 4
        elif tag == "br":
            # End the current line and start a new one.
            self.flush()

    def close_tag(self, tag):
        if tag == "i":
            self.style = "roman"
        elif tag == "b":
            self.weight = "normal"
        elif tag == "small":
            self.size += 2
        elif tag == "big":
            self.size -= 4
        elif tag in self.BLOCK_ELEMENTS:
            # End the current line and start a new one.
            self.flush()
            # Add a gap between paragraphs.
            self.cursor_y += VERTICAL_STEP

    def word(self, word):
        font = self.get_font(self.size, self.weight, self.style)
        w = font.measure(word)

        if self.cursor_x + w > self.width:
            # Wrap text to next line.
            self.cursor_y += font.metrics("linespace") * self.LEADING
            self.cursor_x = HORIZONTAL_STEP
            
            self.flush()

        self.line.append((self.cursor_x, word, font))

        # " " adds back the whitespace that was removed when splitting the text.
        self.cursor_x += w + font.measure(" ")

    def flush(self):
        if not self.line: return
        metrics = [font.metrics() for x, word, font in self.line]

        # The top of the tallest glyph.
        max_ascent = max(metric["ascent"] for metric in metrics)

        baseline = self.cursor_y + self.LEADING * max_ascent

        # Align each word vertically relative to the baseline.
        for rel_x, word, font in self.line:
            x = self.x + rel_x
            y = self.y + baseline - font.metrics("ascent")
            self.display_list.append((x, y, word, font))

        # The bottom of the deepest glyph.
        max_descent = max([metric["descent"] for metric in metrics])

        self.cursor_y = baseline + self.LEADING * max_descent

        self.cursor_x = 0
        self.line = []

    def get_font(self, size, weight, style):
        key = (size, weight, style)

        if key not in self.FONTS:
            font = tkinter.font.Font(size=size, weight=weight, slant=style)
            label = tkinter.Label(font=font)
            self.FONTS[key] = (font, label)

        return self.FONTS[key][0]
    
    def __repr__(self):
        if isinstance(self.node, Text):
            return "BlockLayoutNode('" + self.node.text + "')"
        else:
            return "BlockLayoutNode(" + self.node.tag + ")"
    
