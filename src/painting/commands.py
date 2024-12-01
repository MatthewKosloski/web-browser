from tkinter import Canvas
from tkinter.font import Font

from painting.shapes import Rect

class DrawRect:
    def __init__(self, rect: Rect, color: str) -> None:
        self.rect = rect
        self.color = color

    def execute(self, canvas: Canvas, scroll = 0) -> None:
        canvas.create_rectangle(
            self.rect.left,
            self.rect.top - scroll,
            self.rect.right,
            self.rect.bottom - scroll,
            # Do not draw border.
            width=0,
            fill=self.color)
        
    def __repr__(self) -> str:
        return f"DrawRect(({self.rect.left}, {self.rect.top}), ({self.rect.right}, {self.rect.bottom}), {self.color})"
        
class DrawText:
    def __init__(self, rect: Rect, text: str, font: Font, color: str) -> None:
        rect.bottom = rect.top + font.metrics("linespace")
        self.rect = rect
        self.text = text
        self.font = font
        self.color = color

    def execute(self, canvas: Canvas, scroll = 0) -> None:
        canvas.create_text(
            self.rect.left,
            self.rect.top - scroll,
            text=self.text,
            font=self.font,
            fill=self.color,
            anchor='nw')

    def __repr__(self) -> str:
        return f"DrawText(({self.rect.left}, {self.rect.top}), \"{self.text}\", {self.color})"
    
class DrawOutline:
    def __init__(self, rect: Rect, color: str, thickness: float) -> None:
        self.rect = rect
        self.color = color
        self.thickness = thickness

    def execute(self, canvas: Canvas, scroll = 0) -> None:
        canvas.create_rectangle(
            self.rect.left, self.rect.top - scroll,
            self.rect.right, self.rect.bottom - scroll,
            width = self.thickness,
            outline = self.color)
    
    def __repr__(self) -> str:
        return f"DrawOutline({self.rect}, {self.color}, {self.thickness})"
    
class DrawLine:
    def __init__(self, rect: Rect, color: str, thickness: float) -> None:
        self.rect = rect
        self.color = color
        self.thickness = thickness

    def execute(self, canvas: Canvas, scroll = 0) -> None:
        canvas.create_line(
            self.rect.left, self.rect.top - scroll,
            self.rect.right, self.rect.bottom - scroll,
            fill=self.color, width=self.thickness)
    
    def __repr__(self) -> str:
        return f"DrawLine(({self.x1}, {self.y1}), ({self.x2}, {self.y2}), {self.color}, {self.thickness})"
    
DrawCommand = DrawRect | DrawText | DrawOutline | DrawLine