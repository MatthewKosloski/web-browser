from typing import Dict, List, Tuple

from css.selectors import CSSSelector, TagSelector, DescendantSelector

CSSDeclarations = Dict[str, str]
CSSRule = Tuple[CSSSelector, CSSDeclarations]

class CSSParser:

    def __init__(self, s: str) -> None:
        self.s = s
        self.i = 0

    def whitespace(self) -> None:
        while self.i < len(self.s) and self.s[self.i].isspace():
            self.i += 1

    def word(self) -> str:
        start = self.i

        while self.i < len(self.s):
            if self.s[self.i].isalnum() or self.s[self.i] in "#-.%":
                # Increment i through any word characters
                self.i += 1
            else:
                break
        
        if not (self.i > start):
            raise Exception("Parsing error")
        
        return self.s[start:self.i]
    
    def literal(self, literal: str) -> None:
        if not (self.i < len(self.s) and self.s[self.i] == literal):
            raise Exception("Parsing error")
        self.i += 1

    def pair(self) -> Tuple[str, str]:
        prop = self.word()
        self.whitespace()
        self.literal(":")
        self.whitespace()
        val = self.word()
        return prop.casefold(), val
    
    def body(self) -> CSSDeclarations:
        pairs = {}

        while self.i < len(self.s) and self.s[self.i] != "}":
            try:
                prop, val = self.pair()
                pairs[prop.casefold()] = val
                self.whitespace()
            except Exception:
                # Skip any parse errors (ignore anything we don't understand).
                why = self.ignore_until([";", "}"])

                if why == ";":
                    self.literal(";")
                    self.whitespace()
                else:
                    break
        
        return pairs
    
    def selector(self) -> CSSSelector:
        out = TagSelector(self.word().casefold())
        self.whitespace()
        while self.i < len(self.s) and self.s[self.i] != "{":
            tag = self.word()
            descendant = TagSelector(tag.casefold())
            out = DescendantSelector(out, descendant)
            self.whitespace()
        return out

    def parse(self) -> List[CSSRule]:
        rules: List[CSSRule] = []
        while self.i < len(self.s):
            try:
                self.whitespace()
                selector = self.selector()
                self.literal("{")
                self.whitespace()
                body = self.body()
                self.literal("}")
                rules.append((selector, body))
            except Exception:
                why = self.ignore_until(["}"])
                if why == "}":
                    self.literal("}")
                    self.whitespace()
                else:
                    break
        return rules

    def ignore_until(self, chars: str) -> str | None: 
        while self.i < len(self.s):
            if self.s[self.i] in chars:
                return self.s[self.i]
            else:
                self.i += 1
        return None
    
