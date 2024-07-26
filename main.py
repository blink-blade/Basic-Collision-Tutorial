from pathlib import Path

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import RenderContext
from kivy.uix.effectwidget import AdvancedEffectBase, EffectWidget
from kivy.uix.image import Image

Window.size = (1920, 1080)

parent_dir = Path(__file__).parent
# This is all the characters in the shader file.
brightener_glsl = (parent_dir / 'collision_brightener.glsl').read_text()

# Just using an image because I am lazy.
class Rect(EffectWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.background_color = [1, 1, 1, 1]
        self.size_hint = None, None
        self.brightener_effect = AdvancedEffectBase(glsl=brightener_glsl, uniforms={
            'x': float(self.x)})
        self.effects = [self.brightener_effect]
        Clock.schedule_interval(self.update, 1/60)

    def update(self, dt):
        self.x += 2
        self.brightener_effect.uniforms['x'] = float(self.x)


class GameApp(App):
    def __init__(self, **kwargs):
        super(GameApp, self).__init__(**kwargs)
        # Window.bind(on_motion=on_motion, on_resize=self.on_resize)
        # Window.bind(on_joy_axis=on_joy_axis, on_joy_hat=on_joy_hat, on_joy_ball=on_joy_ball,
        #             on_joy_button_up=on_joy_button_up, on_joy_button_down=on_joy_button_down, on_key_up=on_key_up,
        #             on_key_down=on_key_down, on_touch_down=on_touch_down, on_touch_up=on_touch_up)


    def on_start(self):
        Clock.schedule_interval(self.update, 1 / 60)
        self.rect1 = Rect(pos=(500, 500), size=(200, 200))
        self.root.add_widget(self.rect1)
        # self.rect1 = Rect(pos=(550, 550), size=(200, 200), color=(1, 0, 0, 1))
        # self.root.add_widget(self.rect1)


    def update(self, dt):
        pass


if __name__ == '__main__':
    GameApp().run()
