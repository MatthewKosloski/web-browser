from tkinter import Label, Event
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
        self.urlbar_top = self.tabbar_bottom
        self.urlbar_bottom = self.urlbar_top + \
            self.font_height + 2*self.padding
        self.bottom = self.urlbar_bottom
        back_width = self.font.measure("<") + 2 * self.padding
        self.back_rect = Rect(
            self.padding,
            self.urlbar_top + self.padding,
            self.padding + back_width,
            self.urlbar_bottom - self.padding)
        self.address_rect = Rect(
            self.back_rect.top + self.padding,
            self.urlbar_top + self.padding,
            WINDOW_WIDTH - self.padding,
            self.urlbar_bottom - self.padding)
        self.focus = None
        self.address_bar = ""
        
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
                
        # Paint the back button.
        cmds.append(DrawOutline(self.back_rect, "black", 1))
        cmds.append(DrawText(
            Rect(self.back_rect.left + self.padding, self.back_rect.top),
            "<", self.font, "black"))
        
        # Paint the address bar.
        cmds.append(DrawOutline(self.address_rect, "black", 1))

        if self.focus == "address bar":
            # Draw currently typed text.
            cmds.append(DrawText(
                Rect(self.address_rect.left + self.padding, self.address_rect.top),
                self.address_bar, self.font, "black"))
            # Draw a cursor.
            w = self.font.measure(self.address_bar)
            cmds.append(DrawLine(
                Rect(
                    self.address_rect.left + self.padding + w,
                    self.address_rect.top,
                    self.address_rect.left + self.padding + w,
                    self.address_rect.bottom),
                "red", 1))
        else:
            # Draw the current URL.
            url = str(self.browser.active_tab.url)
            cmds.append(DrawText(
                Rect(self.address_rect.left + self.padding, self.address_rect.top),
                url, self.font, "black"))

        return cmds

    def click(self, x: int, y: int) -> None:
        if self.newtab_rect.containsPoint(x, y):
            self.browser.new_tab(Url("https://browser.engineering/"))
        elif self.back_rect.containsPoint(x, y):
            self.browser.active_tab.go_back()
        elif self.address_rect.containsPoint(x, y):
            self.focus = "address bar"
            self.address_bar = ""
        else:
            for i, tab in enumerate(self.browser.tabs):
                if self.tab_rect(i).containsPoint(x, y):
                    self.browser.active_tab = tab
                    break
    
    def blur(self) -> None:
        self.focus = None

    def keypress(self, e: Event) -> bool:
        """
            Handles keypress. Returns true if the key was
            consumed by the chrome; false otherwise.
        """
        if self.focus == "address bar":
            if e.keysym == "BackSpace":
                # Remove last character.
                self.address_bar = self.address_bar[0:-1]
                return True
            else:
                self.address_bar += e.char
                return True
        
        return False

    def enter(self) -> None:
        if self.focus == "address bar":
            self.browser.active_tab.load(Url(self.address_bar))
            self.focus = None

    def get_font(self, size: int, weight: str, style: str) -> Tuple[Font, Label]:
        key = (size, weight, style)

        if key not in self.FONTS:
            font = Font(size=size, weight=weight, slant=style)
            label = Label(font=font)
            self.FONTS[key] = (font, label)

        return self.FONTS[key][0]