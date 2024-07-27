from pathlib import Path

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import RenderContext, Rectangle, Color
from kivy.uix.effectwidget import AdvancedEffectBase, EffectWidget
from kivy.uix.image import Image

from helpers import get_distance_between_points, controls, on_key_up, on_key_down

Window.size = (1920, 1080)

rects = []
gravity = -0.25

# Just using an image because I am lazy.
class Rect(Image):
    def __init__(self, *args, **kwargs):
        rects.append(self)
        self.x_velocity = 0
        self.y_velocity = 0
        super().__init__(*args, **kwargs)
        self.instructions = []
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

    def solve_with_rect(self, rect):
        intersection_size = get_intersection_of_rects(rect, self)[2:]

        # We solve the axis with the least overlap.
        if intersection_size[0] < intersection_size[1]:
            if self.x > rect.x:
                rect.x -= intersection_size[0]
            else:
                rect.x += intersection_size[0]
        else:
            if self.y > rect.y:
                rect.y -= intersection_size[1]
            else:
                rect.y += intersection_size[1]

    def solve_collisions(self):
        # First, get the rect which is intersecting the most.
        largest_intersection = 0
        rect_to_solve = None
        for rect in rects:
            if rect == self:
                continue
            intersection_size = get_intersection_of_rects(rect, self)[2:]
            area = intersection_size[0] * intersection_size[1]
            if area > largest_intersection:
                largest_intersection = area
                rect_to_solve = rect
        # If there wasn't any intersections, then don't do anything.
        if not largest_intersection:
            return
        # Then we solve collisions with that rect.
        self.solve_with_rect(rect_to_solve)

    def update(self, dt):
        # Apply gravity
        self.y_velocity += gravity

        # We diminish the velocity so that we don't keep moving. We could change how much the velocity is diminished-
        # based on the surface the rect is on.
        self.x_velocity *= 0.98

        # Now move the rect corresponding to its velocity.
        self.x += self.x_velocity
        self.y += self.y_velocity

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
        Window.bind(on_key_up=on_key_up, on_key_down=on_key_down)

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
        self.player_rect = Rect(pos=(500, 500), size=(200, 200), color=(1, 1, 0, 1))
        self.root.add_widget(self.player_rect)

    def update(self, dt):
        if controls.get('space'):
            self.player_rect.solve_collisions()
            controls.pop('space')
        for rect in rects:
            rect.update(dt)


if __name__ == '__main__':
    GameApp().run()
