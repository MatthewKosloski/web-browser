class LineLayoutNode:

    LEADING = 1.25

    def __init__(self, node, parent, previous):
        self.node = node
        self.parent = parent
        self.previous = previous
        self.children = []

    def layout(self):
        # To compute a line's x position, the x position of its parent node
        # must already have been computed. So a line's x must therefore be
        # computed before its children's x.
        self.x = self.parent.x

        # If there is a previous sibling, then layout starts right after
        # that sibling. Otherwise, layout starts at the parent's top edge.
        if self.previous:
            self.y = self.previous.y + self.previous.height
        else:
            self.y = self.parent.y

        self.width = self.parent.width

        for word in self.children:
            word.layout()

        # The top of the tallest glyph.
        max_ascent = max(word.font.metrics("ascent") for word in self.children)

        baseline = self.y + self.LEADING * max_ascent

        # Align each word vertically relative to the baseline.
        for word in self.children:
            word.y = baseline - word.font.metrics("ascent")

        # The bottom of the deepest glyph.
        max_descent = max(word.font.metrics("descent") for word in self.children)

        self.height = self.LEADING * (max_ascent + max_descent)

    def paint(self):
        return []
    
    def __repr__(self):
        return "LineLayoutNode"