from hypertext.nodes import HTMLNode
from typing import List

def log_tree(node: HTMLNode, indent = 0) -> None:
    print(" " * indent, node)
    for child in node.children:
        log_tree(child, indent + 4)

def tree_to_list(tree: HTMLNode, list: List[HTMLNode]) -> List[HTMLNode]:
    list.append(tree)
    for child in tree.children:
        tree_to_list(child, list)
    return list