import math
from tkinter import Event
from typing import Optional

from constants import VERTICAL_STEP, WINDOW_WIDTH, WINDOW_HEIGHT
from painting.commands import DrawRect
from painting.shapes import Rect

class Scrollbar:
    def __init__(self, tab):
        self.tab = tab
        self.scroll = 0
        self.color = "blue"
        self.width = 15
        self.y0 = None
        self.y1 = None
        self.scroll_step = self.calculate_scroll_step()

    def calculate_scroll_distance(self) -> float:
        """
        Calculates the scrollable distance.
        """
        if self.tab.document.height + VERTICAL_STEP > self.tab.height:
            # The height of the web page contents exceeds the height of
            # the viewable area. Therefore, the scrollable distance is
            # the height of the document that's outside the viewable area. 
            distance = self.tab.document.height + VERTICAL_STEP - self.tab.height
        else:
            # All page contents are within the viewport, therefore,
            # the scrollable distance is zero.
            distance = 0

        return distance

    def calculate_scroll_step(self) -> float:
        """
        Calculates the scroll step. That is, by how many vertical points
        we want to move the scroll bar down for each scroll event.
        """

        # We don't want the scroll step to exceed 5% of the viewport height.
        max_scroll_step = math.floor(self.tab.height * 0.05)

        scroll_distance = self.calculate_scroll_distance()

        if scroll_distance > max_scroll_step:
            num_steps = math.floor(scroll_distance / max_scroll_step)
        else:
            # The maximum scrollable distance is less than half
            # the height of the window, therefore, we can complete
            # the scroll in a single step.
            num_steps = 1

        # Find the required number of scroll steps such that
        # the step amount does not exceed half the height of the window.
        while (num_steps > 0 and scroll_distance / num_steps > max_scroll_step):
            num_steps += 1

        # Calculate the required scroll step to complete num_steps of scroll.
        if num_steps > 0:
            scroll_step = scroll_distance / num_steps
        else:
            scroll_step = 0

        return scroll_step
    
    def calculate_height(self) -> float:
        """
        Calculates the scrollbar height. If the maximum scrollable distance
        is zero, then the scrollbar height is zero.
        """

        scroll_distance = self.calculate_scroll_distance()

        if scroll_distance > 0:

            if scroll_distance <= self.tab.height:
                visible_content_percentage = (self.tab.height - scroll_distance) / self.tab.height
            else:
                visible_content_percentage = self.tab.height / scroll_distance
                
            scrollbar_height = visible_content_percentage * self.tab.height
        else:
            # There is no distance to scroll, therefore, there is no scrollbar.
            scrollbar_height = 0

        return scrollbar_height
    
    def get_scroll_steps(self) -> int:
        """
        Returns the number of scroll steps.
        """
        scroll_distance = self.calculate_scroll_distance()

        if self.scroll_step > 0:
            num_steps = int(scroll_distance / self.scroll_step)
        else:
            num_steps = 0

        return num_steps
    
    def draw(self, e: Optional[Event] = None) -> None:
        height = self.calculate_height()

        # We don't need to paint a scrollbar.
        if height <= 0:
            return
        
        display_list = []

        y0_lower_limit = self.tab.browser.chrome.bottom
        y0_upper_limit = WINDOW_HEIGHT - height
        y1_lower_limit = self.tab.browser.chrome.bottom + height
        y1_upper_limit = WINDOW_HEIGHT

        scroll_steps = self.get_scroll_steps()
        step = (self.tab.height - height) / scroll_steps

        if self.y0 is None:
            self.y0 = y0_lower_limit
        elif e is not None and e.keysym == "Down":
            self.y0 += step
        elif e is not None and e.keysym == "Up":
            self.y0 -= step

        if self.y1 is None:
            self.y1 = y1_lower_limit
        elif e is not None and e.keysym == "Down":
            self.y1 += step
        elif e is not None and e.keysym == "Up":
            self.y1 -= step

        # Prevent y0 from exiting window boundary.
        if self.y0 >= y0_upper_limit:
            self.y0 = y0_upper_limit
        elif self.y0 <= y0_lower_limit:
            self.y0 = y0_lower_limit

        # Prevent y1 from exiting window boundary.
        if self.y1 >= y1_upper_limit:
            self.y1 = y1_upper_limit
        elif self.y1 <= y1_lower_limit:
            self.y1 = y1_lower_limit

        x0, y0 = (WINDOW_WIDTH - self.width, self.y0)
        x1, y1 = (WINDOW_WIDTH, self.y1)

        display_list.extend([DrawRect(Rect(x0, y0, x1, y1), self.color)])

        for command in display_list:
            command.execute(self.tab.browser.canvas)
 
    def scroll_down(self) -> None:
        # Check if we have a scrollbar. If not, then don't do anything.
        height = self.calculate_height()
        if height <= 0:
            return

        # Do not scroll down past the page.
        max_scroll = self.tab.document.height + VERTICAL_STEP - WINDOW_HEIGHT + self.tab.browser.chrome.bottom
        if self.scroll + self.scroll_step >= max_scroll:
            self.scroll = max_scroll
        else:
            self.scroll += self.scroll_step

    def scroll_up(self) -> None:
        # Check if we have a scrollbar. If not, then don't do anything.
        height = self.calculate_height()
        if height <= 0:
            return

        # Do not scroll up past the page.
        min_scroll = 0
        if self.scroll - self.scroll_step <= min_scroll:
            self.scroll = min_scroll
        else:
            self.scroll -= self.scroll_step