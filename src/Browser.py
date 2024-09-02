import tkinter

from Url import Url
from Scrollbar import Scrollbar

class Browser:

    def __init__(self, width = 800, height = 600, hstep = 13, vstep = 18):
        self.width = width
        self.height = height
        self.hstep = hstep
        self.vstep = vstep
        self.scrollbar = None
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(
            self.window,
            width=self.width,
            height=self.height
        )
        self.canvas.pack()

        # Bind events to event handlers.
        self.window.bind("<Down>", self.handle_event_down)
        self.window.bind("<Up>", self.handle_event_up)

    def handle_event_down(self, e):
        if self.scrollbar is not None:
            self.scrollbar.scroll_down(e)

        # Erase and redraw the canvas.
        self.canvas.delete("all")
        self.draw(e)

    def handle_event_up(self, e):
        if self.scrollbar is not None:
            self.scrollbar.scroll_up(e)

        # Erase and redraw the canvas.
        self.canvas.delete("all")
        self.draw(e)

    def load(self, url):
        body = url.request()
        text = lex(body)
        self.display_list = layout(text, self.width, self.hstep, self.vstep)
        self.scrollbar = Scrollbar(
            canvas=self.canvas,
            window_width=self.width,
            window_height=self.height,
            vstep=self.vstep,
            max_y=self.display_list[-1][1])
        self.draw()

    def to_screen_coordinate(self, page_coordinate):
        page_x, page_y = page_coordinate
        screen_x, screen_y = (page_x, page_y - self.scrollbar.scroll)

        return (screen_x, screen_y)

    def draw(self, e = None):
        self.scrollbar.draw_scrollbar(e)

        for page_x, page_y, c in self.display_list:

            # Skip drawing characters that are offscreen.
            if page_y > self.scrollbar.scroll + self.height: continue
            if page_y + self.vstep < self.scrollbar.scroll: continue

            screen_x, screen_y = self.to_screen_coordinate((page_x, page_y))
            self.canvas.create_text(screen_x, screen_y, text=c)

'''
  Computes and stores the position of each character, storing
  it in a display list. This function operates using page coordinates.
'''
def layout(text, window_width, hstep = 13, vstep = 18):
    display_list = []
    cursor_x, cursor_y = hstep, vstep

    for c in text:
        display_list.append((cursor_x, cursor_y, c))
        cursor_x += hstep
        # Wrap the text once we reach the edge of the screen.
        # The ICU Library, used by both Firefox and Chrome, uses
        # dynamic programming to guess phase boundaries based on
        # a word frequency table.
        # https://site.icu-project.org/
        # https://github.com/unicode-org/icu/blob/master/icu4c/source/data/brkitr/dictionaries/cjdict.txt
        if cursor_x >= window_width - hstep:
            cursor_y += vstep
            cursor_x = hstep

    return display_list

def lex(body):
    text = ""
    in_tag = False
    for c in body:
        if c == "<":
            in_tag = True
        elif c == ">":
            in_tag = False
        elif not in_tag:
            text += c
    return text

if __name__ == "__main__":
    import sys
    url = sys.argv[1]
    Browser().load(Url(url))
    tkinter.mainloop()