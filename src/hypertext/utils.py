from hypertext.nodes import HTMLNode

def log_tree(node: HTMLNode, indent = 0) -> None:
    print(" " * indent, node)
    for child in node.children:
        log_tree(child, indent + 4)