import tkinter
from tkinter import Canvas, Event
from typing import Optional

from chrome.chrome import Chrome
from chrome.tab import Tab
from constants import WINDOW_WIDTH, WINDOW_HEIGHT
from url.url import Url

class Browser:

    def __init__(self) -> None:
        self.tabs = []
        self.active_tab = None
        self.window = tkinter.Tk()
        self.canvas = Canvas(
            self.window,
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT,
            bg="white")
        self.canvas.pack()
        self.chrome = Chrome(self)

        # Bind events to event handlers.
        self.window.bind("<Down>", self.handle_event_down)
        self.window.bind("<Up>", self.handle_event_up)
        self.window.bind("<Button-1>", self.handle_event_click)
        self.window.bind("<Key>", self.handle_key)
        self.window.bind("<Return>", self.handle_enter)

    def new_tab(self, url: str) -> None:
        new_tab = Tab(self)
        new_tab.load(url)
        self.active_tab = new_tab
        self.tabs.append(new_tab)
        self.draw()

    def draw(self, e: Optional[Event] = None) -> None:
        self.canvas.delete("all")
        self.active_tab.draw(e)

        # Draw the chrome after the tab contents, so that
        # the chrome is drawn over it.
        for cmd in self.chrome.paint():
            cmd.execute(self.canvas, 0)

    def handle_event_down(self, e: Event) -> None:
        self.active_tab.scroll_down()
        self.draw(e)

    def handle_event_up(self, e: Event) -> None:
        self.active_tab.scroll_up()
        self.draw(e)

    def handle_event_click(self, e: Event) -> None:
        if e.y < self.chrome.bottom:
            # Delegate clicks on the browser chrome to the Chrome object.
            self.chrome.click(e.x, e.y)
        else:
            # Delegate any other click to the active tab.
            tab_y = e.y - self.chrome.bottom
            self.active_tab.click(e.x, tab_y)
        self.draw()

    def handle_key(self, e: Event) -> None:
        # Ignore when no character is typed.
        if len(e.char) == 0: return

        self.chrome.keypress(e)
        self.draw()

    def handle_enter(self, e: Event) -> None:
        self.chrome.enter()
        self.draw()

if __name__ == "__main__":
    import sys
    Browser().new_tab(Url(sys.argv[1]))
    tkinter.mainloop()