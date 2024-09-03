from Text import Text
from Element import Element

class HTMLParser:

    SELF_CLOSING_TAGS = [
        "area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "param", "source", "track", "wbr",
    ]

    HEAD_TAGS = [
        "base", "basefont", "bgsound", "noscript",
        "link", "meta", "title", "style", "script",
    ]

    def __init__(self, body):
        self.body = body
        self.unfinished = []

    def parse(self):
        text = ""
        in_tag = False
        for c in self.body:
            if c == "<":
                in_tag = True
                if text: self.add_text(text)
                text = ""
            elif c == ">":
                in_tag = False
                self.add_tag(text)
                text = ""
            else:
                text += c
        if not in_tag and text:
            self.add_text(text)
        return self.finish()
    
    def add_text(self, text):

        # Skip whitespace-only text nodes. Note: real browsers
        # don't do this -- they retain whitespace.
        if text.isspace(): return

        self.implicit_tags(None)

        parent = self.unfinished[-1]
        node = Text(text, parent)
        parent.children.append(node)

    def add_tag(self, tag):

        tag, attributes = self.get_attributes(tag)

        # Discard the doctype.
        if tag.startswith("!"): return

        self.implicit_tags(tag)

        if tag.startswith("/"):
            # The very last tag does not get added to a node.
            if len(self.unfinished) == 1: return

            # Closing tag.
            # Finish the last unfinished node by adding it to
            # the previous unfinished node in the list.
            node = self.unfinished.pop()
            parent = self.unfinished[-1]
            parent.children.append(node)
        elif tag in self.SELF_CLOSING_TAGS:
            # Auto-close a self-closing tag.
            parent = self.unfinished[-1]
            node = Element(tag, attributes, parent)
            parent.children.append(node)
        else:
            # Opening tag.
            # Add an unfinished node to the end of the list.
            parent = self.unfinished[-1] if self.unfinished else None
            node = Element(tag, attributes, parent)
            self.unfinished.append(node)

    def finish(self):
        if not self.unfinished:
            self.implicit_tags(None)

        while len(self.unfinished) > 1:
            node = self.unfinished.pop()
            parent = self.unfinished[-1]
            parent.children.append(node)
        return self.unfinished.pop()
    
    def implicit_tags(self, tag):
        while True:
            open_tags = [node.tag for node in self.unfinished]

            # The first tag in the document is something other than html.
            if open_tags == [] and tag != "html":
                self.add_tag("html")
            elif open_tags == ["html"] \
                and tag not in ["head", "body", "/html"]:
                if tag in self.HEAD_TAGS:
                    self.add_tag("head")
                else:
                    self.add_tag("body")
            # If inside the head and an element that's supposed
            # to go in the <body> is encountered.
            elif open_tags == ["html", "head"] and \
                tag not in ["/head"] + self.HEAD_TAGS:
                self.add_tag("/head")
            else:
                break
    
    def get_attributes(self, text):
        parts = text.split()
        tag = parts[0].casefold()
        attributes = {}
        for attrpair in parts[:1]:
            if "=" in attrpair:
                # Unquoted attribute.
                key, value = attrpair.split("=", 1)

                # Quoted attribute -- strip out quotes.
                if len(value) > 2 and value[0] in ["'", "\""]:
                    value = value[1:-1]

                attributes[key.casefold()] = value
            else:
                # Attribute value is omitted.
                attributes[attrpair.casefold()] = ""
        return tag, attributes