from pathlib import Path

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import RenderContext, Rectangle, Color
from kivy.uix.effectwidget import AdvancedEffectBase, EffectWidget
from kivy.uix.image import Image

from helpers import get_distance_between_points

Window.size = (1920, 1080)

rects = []

# Just using an image because I am lazy.
class Rect(Image):
    def __init__(self, *args, **kwargs):
        rects.append(self)
        super().__init__(*args, **kwargs)
        self.instructions = []
        self.background_color = [1, 1, 1, 1]
        self.size_hint = None, None


    def remove_extra_instructions(self):
        for instruction in self.instructions:
            self.canvas.remove(instruction)
        self.instructions.clear()


    def add_instructions(self):
        for rect in rects:
            if rect == self:
                continue
            intersection = get_intersection_of_rects(rect, self)
            if intersection[2] * intersection[3] > 0:
                color = Color(1, 0.5, 1, 1)
                brightener_instruction = Rectangle()
                self.instructions.append(brightener_instruction)
                brightener_instruction.pos = intersection[0], intersection[1]
                brightener_instruction.size = intersection[2], intersection[3]
                self.canvas.add(color)
                self.canvas.add(brightener_instruction)


    def update(self, dt):
        self.remove_extra_instructions()
        self.add_instructions()


def get_intersection_of_rects(rect_one, rect_two):
    # This function gets the area of intersection between two rects.
    intersection_left = max(rect_one.x, rect_two.x)
    intersection_bottom = max(rect_one.y, rect_two.y)
    intersection_right = min(rect_one.right, rect_two.right)
    intersection_top = min(rect_one.top, rect_two.top)
    intersection_width = intersection_right - intersection_left
    intersection_height = intersection_top - intersection_bottom

    # If there is an intersection, return the variables.
    if intersection_width > 0 and intersection_height > 0:
        return [intersection_left, intersection_bottom, intersection_width, intersection_height]
    # If there isn't an intersection, return this.
    return [0, 0, 0, 0]

    # For more practical use in gamedev or something else, you could use this which just gets the area:
        # intersection = [0, 0]
        # intersection[0] = min(rect_one.right, rect_two.right) - max(rect_one.x, rect_two.x)
        # intersection[1] = min(rect_one.top, rect_two.top) - max(rect_one.y, rect_two.y)
        # return intersection


class GameApp(App):
    def __init__(self, **kwargs):
        self.selected_rect = None
        self.previous_touch_position = None
        super(GameApp, self).__init__(**kwargs)
        # Window.bind(on_motion=on_motion, on_resize=self.on_resize)
        # Window.bind(on_joy_axis=on_joy_axis, on_joy_hat=on_joy_hat, on_joy_ball=on_joy_ball,
        #             on_joy_button_up=on_joy_button_up, on_joy_button_down=on_joy_button_down, on_key_up=on_key_up,
        #             on_key_down=on_key_down, on_touch_down=on_touch_down, on_touch_up=on_touch_up)


    def on_touch_down(self, touch):
        shortest_distance = 10000
        closest_rect = None
        for rect in rects:
            if rect.collide_point(touch.x, touch.y):
                if get_distance_between_points((rect.x, rect.y), (touch.x, touch.y)) < shortest_distance:
                    closest_rect = rect
        self.selected_rect = closest_rect
        self.previous_touch_position = touch.pos


    def on_touch_move(self, touch):
        if not self.selected_rect:
            return
        self.selected_rect.x += touch.x - self.previous_touch_position[0]
        self.selected_rect.y += touch.y - self.previous_touch_position[1]
        self.previous_touch_position = touch.pos
        # This makes things look cleaner when moving the rectangles arouned
        self.update(0)


    def on_touch_up(self, touch):
        self.selected_rect = None


    def on_start(self):
        self.root.on_touch_down = self.on_touch_down
        self.root.on_touch_move = self.on_touch_move
        self.root.on_touch_up = self.on_touch_up
        Clock.schedule_interval(self.update, 1 / 60)
        self.rect1 = Rect(pos=(500, 500), size=(200, 200), color=(0, 1, 0, 1))
        self.root.add_widget(self.rect1)
        self.rect2 = Rect(pos=(550, 550), size=(200, 200), color=(1, 0, 0, 1))
        self.root.add_widget(self.rect2)


    def update(self, dt):
        for rect in rects:
            rect.update(dt)


if __name__ == '__main__':
    GameApp().run()
