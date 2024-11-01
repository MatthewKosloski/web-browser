from .block_layout_node import BlockLayoutNode
from constants import WINDOW_WIDTH, HORIZONTAL_STEP, VERTICAL_STEP

class DocumentLayoutNode:
    def __init__(self, node):
        self.node = node

        self.parent = None
        self.children = []
        self.x = None
        self.y = None
        self.width = None
        self.height = None

    def layout(self):
        self.width = WINDOW_WIDTH - 2 * HORIZONTAL_STEP
        self.x = HORIZONTAL_STEP
        self.y = VERTICAL_STEP

        child = BlockLayoutNode(self.node, self, None)
        self.children.append(child)
        child.layout()

        self.height = child.height

    def paint(self):
        return []
    
    def __repr__(self):
        return "DocumentLayoutNode"