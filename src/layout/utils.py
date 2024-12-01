from typing import List

from layout.layout_node import LayoutNode

def tree_to_list(tree: LayoutNode, list: List[LayoutNode]) -> List[LayoutNode]:
    list.append(tree)
    for child in tree.children:
        tree_to_list(child, list)
    return list

def log_tree(node: LayoutNode, indent = 0) -> None:
    print(" " * indent, node)
    for child in node.children:
        log_tree(child, indent + 4)