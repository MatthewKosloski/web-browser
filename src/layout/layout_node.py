from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List 
from painting.commands import DrawCommand

from hypertext.nodes import HTMLNode

class LayoutNode(ABC):
    def __init__(self, node: HTMLNode, parent: LayoutNode = None, previous: LayoutNode = None) -> None:
        self.node = node
        self.parent = parent
        self.previous = previous
        self.children: List[LayoutNode] = []
        self.x = None
        self.y = None
        self.width = None
        self.height = None

    @abstractmethod
    def layout() -> None:
        pass

    @abstractmethod
    def should_paint() -> bool:
        pass

    @abstractmethod
    def paint() -> List[DrawCommand]:
        pass