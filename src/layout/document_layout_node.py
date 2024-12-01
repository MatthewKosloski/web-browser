from constants import WINDOW_WIDTH, HORIZONTAL_STEP, VERTICAL_STEP
from hypertext.nodes import Element
from layout.block_layout_node import BlockLayoutNode
from layout.layout_node import LayoutNode

class DocumentLayoutNode(LayoutNode):
    def __init__(self, node: Element) -> None:
        super().__init__(node, None, None)

    def layout(self) -> None:
        self.width = WINDOW_WIDTH - 2 * HORIZONTAL_STEP
        self.x = HORIZONTAL_STEP
        self.y = VERTICAL_STEP

        child = BlockLayoutNode(self.node, self, None)
        self.children.append(child)
        child.layout()

        self.height = child.height

    def paint(self) -> list:
        return []
    
    def __repr__(self) -> str:
        return "DocumentLayoutNode"