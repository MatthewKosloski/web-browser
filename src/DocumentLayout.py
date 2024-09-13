from BlockLayout import BlockLayout

class DocumentLayout:
    def __init__(self, config, node):
        self.config = config
        self.node = node

        self.parent = None
        self.children = []
        self.x = None
        self.y = None
        self.width = None
        self.height = None

    def layout(self):
        self.width = self.config.width - 2 * self.config.hstep
        self.x = self.config.hstep
        self.y = self.config.vstep

        child = BlockLayout(self.config, self.node, self, None)
        self.children.append(child)
        child.layout()

        self.height = child.height

    def paint(self):
        return []