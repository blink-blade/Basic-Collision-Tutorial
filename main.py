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

# Just using an image because I am lazy.
class Rect(Image):
    def __init__(self, static, *args, **kwargs):
        self.static = static
        rects.append(self)
        self.x_velocity = 0
        self.y_velocity = 0
        super().__init__(*args, **kwargs)
        self.size_hint = None, None


    def solve_with_rect(self, rect):
        intersection_size = get_intersection_of_rects(rect, self)[2:]

        # We solve the axis with the least overlap.
        if intersection_size[0] < intersection_size[1]:
            # The rect ran into something so it's velocity is set to 0.
            self.x_velocity = 0
            if self.x < rect.x:
                self.x -= intersection_size[0]
            else:
                self.x += intersection_size[0]
        else:
            # The rect ran into something so it's velocity is set to 0.
            self.y_velocity = 0
            if self.y < rect.y:
                self.y -= intersection_size[1]
            else:
                self.y += intersection_size[1]

    def solve_collisions(self):
        # We just start it as a negligible amount so the while loop works.
        largest_intersection = 0.01
        while largest_intersection > 0:
            # First, get the rect which is intersecting the most.`
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
        # We diminish the velocity so that we don't keep moving. We could change how much the velocity is diminished-
        # based on the surface the rect is on.
        self.x_velocity *= 0.9
        self.y_velocity *= 0.9

        # Now move the rect corresponding to its velocity, but we don't move the rect if it is static.
        if not self.static:
            self.x += self.x_velocity
            self.y += self.y_velocity
            self.solve_collisions()


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
        super(GameApp, self).__init__(**kwargs)
        # Window.bind(on_motion=on_motion, on_resize=self.on_resize)
        Window.bind(on_key_up=on_key_up, on_key_down=on_key_down)

    def on_start(self):
        Clock.schedule_interval(self.update, 1 / 60)
        self.player_rect = Rect(pos=(500, 500), size=(200, 200), color=(1, 1, 0, 1), static=False)
        self.root.add_widget(self.player_rect)
        for i in range(30):
            rect = Rect(pos=(i * (1920/30), 0), size=(1920 / 30, 1920 / 30), color=(i % 2, 0, 1, 1), static=True)
            self.root.add_widget(rect)
        for i in range(30):
            rect = Rect(pos=(i * (1920/30), 1080 - (1920/30)), size=(1920 / 30, 1920 / 30), color=(i % 2, 0, 1, 1), static=True)
            self.root.add_widget(rect)
        for i in range(30):
            rect = Rect(pos=(0, i * (1920/30)), size=(1920 / 30, 1920 / 30), color=(i % 2, 0, 1, 1), static=True)
            self.root.add_widget(rect)
        for i in range(30):
            rect = Rect(pos=(200 + (1920/30), i * (1920/30) + 300), size=(1920 / 30, 1920 / 30), color=(i % 2, 0, 1, 1), static=True)
            self.root.add_widget(rect)


    def update(self, dt):
        for rect in rects:
            rect.update(dt)

        if controls.get('a'):
            self.player_rect.x_velocity = -5
        if controls.get('d'):
            self.player_rect.x_velocity = 5
        if controls.get('s'):
            self.player_rect.y_velocity = -5
        if controls.get('w'):
            self.player_rect.y_velocity = 5


if __name__ == '__main__':
    GameApp().run()
