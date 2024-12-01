from tkinter import Label
from tkinter.font import Font
from typing import List, Tuple

from constants import WINDOW_WIDTH
from painting.commands import DrawCommand, DrawLine, DrawOutline, DrawRect, DrawText
from painting.shapes import Rect
from url.url import Url

class Chrome:

    FONTS = {}

    def __init__(self, browser):
        self.browser = browser
        self.font = self.get_font(20, "normal", "roman")
        self.font_height = self.font.metrics("linespace")
        self.padding = 5
        self.tabbar_top = 0
        self.tabbar_bottom = self.font_height + 2 * self.padding
        plus_width = self.font.measure("+") + 2 * self.padding
        self.newtab_rect = Rect(
            self.padding, self.padding,
            self.padding + plus_width,
            self.padding + self.font_height)
        self.bottom = self.tabbar_bottom
        
    def tab_rect(self, i: int) -> Rect:
        tabs_start = self.newtab_rect.right + self.padding
        tab_width = self.font.measure("Tab X") + 2 * self.padding
        return Rect(
            tabs_start + tab_width * i, self.tabbar_top,
            tabs_start + tab_width * (i + 1), self.tabbar_bottom)
    
    def paint(self) -> List[DrawCommand]:
        cmds: List[DrawCommand] = []
        
        # Make sure the chrome is always drawn on top of the page contents.
        # To guarantee that, we can draw a white rectangle behind the chrome.
        cmds.append(DrawRect(
            Rect(0, 0, WINDOW_WIDTH, self.bottom),
            "white"))
        cmds.append(DrawLine(
            Rect(0, self.bottom, WINDOW_WIDTH,
            self.bottom), "black", 1))
        
        # Paint the new-tab button.
        cmds.append(DrawOutline(self.newtab_rect, "black", 1))
        cmds.append(DrawText(
            Rect(self.newtab_rect.left + self.padding,
            self.newtab_rect.top),
            "+", self.font, "black"))
        
        # Paint the tabs.
        for i, tab in enumerate(self.browser.tabs):
            bounds = self.tab_rect(i)
            cmds.append(DrawLine(
                Rect(bounds.left, 0, bounds.left, bounds.bottom),
                "black", 1))
            cmds.append(DrawLine(
                Rect(bounds.right, 0, bounds.right, bounds.bottom),
                "black", 1))
            cmds.append(DrawText(
                Rect(bounds.left + self.padding, bounds.top + self.padding),
                "Tab {}".format(i), self.font, "black"))
            
            # Paint active state above the active tab.
            if tab == self.browser.active_tab:
                cmds.append(DrawLine(
                    Rect(0, bounds.bottom, bounds.left, bounds.bottom),
                    "black", 1))
                cmds.append(DrawLine(
                    Rect(bounds.right, bounds.bottom, WINDOW_WIDTH, bounds.bottom),
                    "black", 1))
        return cmds

    def click(self, x: int, y: int) -> None:
        if self.newtab_rect.containsPoint(x, y):
            self.browser.new_tab(Url("https://browser.engineering/"))
        else:
            for i, tab in enumerate(self.browser.tabs):
                if self.tab_rect(i).containsPoint(x, y):
                    self.browser.active_tab = tab
                    break

    def get_font(self, size: int, weight: str, style: str) -> Tuple[Font, Label]:
        key = (size, weight, style)

        if key not in self.FONTS:
            font = Font(size=size, weight=weight, slant=style)
            label = Label(font=font)
            self.FONTS[key] = (font, label)

        return self.FONTS[key][0]