import tkinter
import tkinter.font

from Element import Element
from Text import Text

class Layout:

    LEADING = 1.25
    FONTS = {}

    def __init__(self, nodes, hstep, vstep, window_width):
        self.display_list = []
        self.line = []
        self.hstep = hstep
        self.vstep = vstep
        self.window_width = window_width
        self.cursor_x = hstep
        self.cursor_y = vstep
        self.weight = "normal"
        self.style = "roman"
        self.size = 12

        self.recurse(nodes)

        self.flush()

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
        elif tag == "p":
            # End the current line and start a new one.
            self.flush()
            # Add a gap between paragraphs.
            self.cursor_y += self.vstep

    def word(self, word):
        font = self.get_font(self.size, self.weight, self.style)
        w = font.measure(word)

        if self.cursor_x + w > self.window_width - self.hstep:
            # Wrap text to next line.
            self.cursor_y += font.metrics("linespace") * self.LEADING
            self.cursor_x = self.hstep
            
            self.flush()

        # self.display_list.append((self.cursor_x, self.cursor_y, word, font))
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
        for x, word, font in self.line:
            y = baseline - font.metrics("ascent")
            self.display_list.append((x, y, word, font))

        # The bottom of the deepest glyph.
        max_descent = max([metric["descent"] for metric in metrics])

        self.cursor_y = baseline + self.LEADING * max_descent

        self.cursor_x = self.hstep
        self.line = []

    def get_font(self, size, weight, style):
        key = (size, weight, style)

        if key not in self.FONTS:
            font = tkinter.font.Font(size=size, weight=weight, slant=style)
            label = tkinter.Label(font=font)
            self.FONTS[key] = (font, label)

        return self.FONTS[key][0]
    
