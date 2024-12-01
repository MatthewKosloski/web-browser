from __future__ import annotations

from typing import List

class HTMLNode:
    def __init__(self, parent: HTMLNode) -> None:
        self.parent = parent
        self.children: List[HTMLNode] = []

class Element(HTMLNode):
    def __init__(self, tag: str, attributes, parent: HTMLNode):
        super().__init__(parent)
        self.tag = tag
        self.attributes = attributes

    def __repr__(self) -> str:
        return "<" + self.tag + ">"
    
class Text(HTMLNode):
    def __init__(self, text, parent: HTMLNode):
        super().__init__(parent)
        self.text = text

    def __repr__(self) -> str:
        return repr(self.text)