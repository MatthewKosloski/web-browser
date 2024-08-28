import math

class Scrollbar:
    def __init__(self, canvas, window_width, window_height, vstep, max_y):
        self.canvas = canvas
        self.window_width = window_width
        self.window_height = window_height
        self.vstep = vstep
        self.max_y = max_y
        self.scroll = 0
        self.scrollbar_color = "blue"
        self.scrollbar_width = 15
        self.scrollbar_y0 = None
        self.scrollbar_y1 = None
        self.scroll_step = self.calculate_scroll_step()

    def calculate_scroll_distance(self):
        """
        Calculates the scrollable distance.
        """
        if self.max_y + self.vstep > self.window_height:
            distance = self.max_y + self.vstep - self.window_height
        else:
            # All page contents are within the viewport, therefore,
            # the scrollable distance is zero.
            distance = 0

        return distance

    def calculate_scroll_step(self):
        """
        Calculates the scroll step. That is, by how many vertical points
        we want to move the scroll bar down for each scroll event.
        """

        # We don't want the scroll step to exceed half the height of the window.
        max_scroll_step = math.floor(self.window_height / 2)

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
    
    def calculate_scrollbar_height(self):
        """
        Calculates the scrollbar height. If the maximum scrollable distance
        is zero, then the scrollbar height is zero.
        """

        scroll_distance = self.calculate_scroll_distance()

        if scroll_distance > 0:

            if scroll_distance <= self.window_height:
                visible_content_percentage = (self.window_height - scroll_distance) / self.window_height
            else:
                visible_content_percentage = self.window_height / scroll_distance
                
            scrollbar_height = visible_content_percentage * self.window_height
        else:
            # There is no distance to scroll, therefore, there is no scrollbar.
            scrollbar_height = 0

        return scrollbar_height
    
    def get_scroll_steps(self):
        """
        Returns the number of scroll steps.
        """
        scroll_distance = self.calculate_scroll_distance()

        if self.scroll_step > 0:
            num_steps = int(scroll_distance / self.scroll_step)
        else:
            num_steps = 0

        return num_steps
 
    def draw_scrollbar(self, e = None):
        scrollbar_height = self.calculate_scrollbar_height()

        # We don't need to draw a scrollbar.
        if scrollbar_height <= 0:
            return

        y0_lower_limit = 0
        y0_upper_limit = self.window_height - scrollbar_height
        y1_lower_limit = scrollbar_height
        y1_upper_limit = self.window_height

        scroll_steps = self.get_scroll_steps()
        y0_step = (y0_upper_limit - y0_lower_limit) / scroll_steps
        y1_step = (y1_upper_limit - y1_lower_limit) / scroll_steps

        if self.scrollbar_y0 is None:
            self.scrollbar_y0 = 0
        if e is not None and e.keysym == "Down":
            self.scrollbar_y0 += y0_step
        elif e is not None and e.keysym == "Up":
            self.scrollbar_y0 -= y0_step

        
        if self.scrollbar_y1 is None:
            self.scrollbar_y1 = scrollbar_height
        elif e is not None and e.keysym == "Down":
            self.scrollbar_y1 += y1_step
        elif e is not None and e.keysym == "Up":
            self.scrollbar_y1 -= y1_step

        # Prevent y0 from exiting boundary.
        if self.scrollbar_y0 >= y0_upper_limit:
            self.scrollbar_y0 = y0_upper_limit
        elif self.scrollbar_y0 <= y0_lower_limit:
            self.scrollbar_y0 = y0_lower_limit

        # Prevent y1 from exiting boundary.
        if self.scrollbar_y1 >= y1_upper_limit:
            self.scrollbar_y1 = y1_upper_limit
        elif self.scrollbar_y1 <= y1_lower_limit:
            self.scrollbar_y1 = y1_lower_limit

        x0, y0 = (self.window_width - self.scrollbar_width, self.scrollbar_y0)
        x1, y1 = (self.window_width, self.scrollbar_y1)

        self.canvas.create_rectangle(x0, y0, x1, y1, fill = self.scrollbar_color, width = 0)

    def scroll_down(self, e):
        # Check if we have a scrollbar. If not, then don't do anything.
        scrollbar_height = self.calculate_scrollbar_height()
        if scrollbar_height <= 0:
            return

        # Do not scroll down past the page.
        max_scroll = self.max_y + self.vstep - self.window_height
        if self.scroll + self.scroll_step >= max_scroll:
            self.scroll = max_scroll
        else:
            self.scroll += self.scroll_step

    def scroll_up(self, e):
        # Check if we have a scrollbar. If not, then don't do anything.
        scrollbar_height = self.calculate_scrollbar_height()
        if scrollbar_height <= 0:
            return

        # Do not scroll up past the page.
        min_scroll = 0
        if self.scroll - self.scroll_step <= min_scroll:
            self.scroll = min_scroll
        else:
            self.scroll -= self.scroll_step