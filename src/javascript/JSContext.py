import dukpy
import os

from css.parser import CSSParser
from hypertext.utils import tree_to_list
from hypertext.parser import HTMLParser

class JSContext:

    def __init__(self, tab):
        self.tab = tab

        self.node_to_handle = {}
        self.handle_to_node = {}

        self.interp = dukpy.JSInterpreter()
        runtime_file = os.path.join(os.path.dirname(__file__), "runtime.js")
        self.runtime = open(runtime_file).read()

        self.interp.evaljs(self.runtime)

        self.interp.export_function("log", print)
        self.interp.export_function("querySelectorAll", self.querySelectorAll)
        self.interp.export_function("getAttribute", self.getAttribute)
        self.interp.export_function("innerHTML_set", self.innerHTML_set)

    def run(self, code: str):
        try:
            return self.interp.evaljs(code)
        except dukpy.JSRuntimeError as e:
            print("Script crashed", e)

    def get_handle(self, elt):
        if elt not in self.node_to_handle:
            handle = len(self.node_to_handle)
            self.node_to_handle[elt] = handle
            self.handle_to_node[handle] = elt
        else:
            handle = self.node_to_handle[elt]

        return handle

    def querySelectorAll(self, selector_text: str) -> None:
        selector = CSSParser(selector_text).selector()

        nodes = [
            node for node
            in tree_to_list(self.tab.nodes, [])
            if selector.matches(node)]
        
        return [
            self.get_handle(node) for node in nodes
        ]
    
    def getAttribute(self, handle, attr):
        elt = self.handle_to_node[handle]
        attr = elt.attributes.get(attr, None)
        return attr if attr else ""
    
    def dispatch_event(self, event, elt):
        handle = self.node_to_handle.get(elt, -1)
        do_default = self.interp.evaljs(
            "new Node(dukpy.handle).dispatchEvent(new Event(dukpy.type))",
            handle=handle,
            type=event)
        return not do_default
        
    def innerHTML_set(self, handle, s):
        doc = HTMLParser("<html><body>" + s + "</body></html>").parse()

        # The new node is the child of the body.
        new_nodes = doc.children[0].children

        # Set the new top-level node of the element.
        elt = self.handle_to_node[handle]
        elt.children = new_nodes

        # Update parent pointers of children to point to
        # the child of the body.
        for child in elt.children:
            child.parent = elt

        self.tab.render()