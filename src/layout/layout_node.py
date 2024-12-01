from __future__ import annotations

from hypertext.nodes import Element, Text

class LayoutNode:
    def __init__(self, node: Element | Text, parent: LayoutNode = None, previous: LayoutNode = None) -> None:
        self.node = node
        self.parent = parent
        self.previous = previous
        self.children = []
        self.x = None
        self.y = None
        self.width = None
        self.height = None

