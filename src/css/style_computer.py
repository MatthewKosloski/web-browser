import os

from css.parser import CSSParser
from hypertext.nodes import Element

INHERITED_PROPERTIES = {
    "font-size": "16px",
    "font-style": "normal",
    "font-weight": "normal",
    "color": "black",
}

class StyleComputer:

    def __init__(self, html, url):
        self.html = html
        self.url = url
        self.rules = sorted(self.get_rules(), key=self.cascade_priority)

    def compute_style(self, node):
        node.style = {}

        # Apply inherited properties to the node.
        for property, default_value in INHERITED_PROPERTIES.items():
            if node.parent:
                node.style[property] = node.parent.style[property]
            else:
                node.style[property] = default_value

        # Apply style sheet rules to the node.
        for selector, body in self.rules:
            if not selector.matches(node): continue
            for property, value in body.items():
                node.style[property] = value

        # Apple style attribute rules to the node.
        if isinstance(node, Element) and "style" in node.attributes:
            pairs = CSSParser(node.attributes["style"]).body()

            for property, value in pairs.items():
                node.style[property] = value

        # Resolve font-size percentages to absolute pixel units.
        if node.style["font-size"].endswith("%"):
            if node.parent:
                parent_font_size = node.parent.style["font-size"]
            else:
                parent_font_size = INHERITED_PROPERTIES["font-size"]
            node_pct = float(node.style["font-size"][:-1]) / 100
            parent_px = float(parent_font_size[:-2])
            node.style["font-size"] = str(node_pct * parent_px) + "px"

        # Compute style of children.
        for child in node.children:
            self.compute_style(child)
    
    def get_rules(self):
        rules = self.get_user_agent_rules()
        rules.extend(self.get_linked_stylesheet_rules())
        return rules
    
    def get_user_agent_rules(self):
        default_stylesheet_path = os.path.join(os.path.dirname(__file__), "browser.css")
        default_stylesheet_content = open(default_stylesheet_path).read()
        rules = CSSParser(default_stylesheet_content).parse().copy()
        return rules
            
    def get_linked_stylesheet_rules(self):
        rules = []
        for link in self.get_linked_stylesheets():
            style_url = self.url.resolve(link)
            try:
                body = style_url.request()
            except:
                # Ignore stylesheets that fail to download.
                continue

            rules.extend(CSSParser(body).parse())
        return rules
    
    def get_linked_stylesheets(self):
        node_list = self.tree_to_list(self.html, [])
        links = []
        for node in node_list:
            if isinstance(node, Element) \
            and node.tag == "link" \
            and node.attributes.get("rel") == "stylesheet" \
            and "href" in node.attributes:
                links.append(node.attributes["href"])
        return links

    def tree_to_list(self, tree, list):
        list.append(tree)
        for child in tree.children:
            self.tree_to_list(child, list)
        return list
    
    def cascade_priority(self, rule):
        selector, body = rule
        return selector.priority