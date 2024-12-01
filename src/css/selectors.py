from hypertext.nodes import HTMLNode, Element

class CSSSelector:
    def __init__(self, priority: int) -> None:
        self.priority = priority

class TagSelector(CSSSelector):
    def __init__(self, tag: str) -> None:
        super().__init__(1)
        self.tag = tag

    def matches(self, node: HTMLNode) -> bool:
        return isinstance(node, Element) and self.tag == node.tag

class DescendantSelector(CSSSelector):
    def __init__(self, ancestor: CSSSelector, descendant: CSSSelector) -> None:
        super().__init__(ancestor.priority + descendant.priority)
        self.ancestor = ancestor
        self.descendant = descendant
    
    def matches(self, node: HTMLNode) -> bool:
        if not self.descendant.matches(node): return False
        while node.parent:
            if self.ancestor.matches(node.parent): return True
            node = node.parent
        return False