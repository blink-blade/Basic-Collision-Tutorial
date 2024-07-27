def get_distance_between_points(one, two):
    return abs(one[0] - two[0]) + abs(one[1] - two[1])


# From here on is just control stuff to ingore.
keyboard_mapping = {
    32: 'space',
    97: 'a',
    119: 'w',
    100: 'd',
    115: 's',
    27: 'escape',
    118: 'v',
    120: 'x',
    121: 'y',
    9: 'tab',
    98: 'b',
    107: 'k',
}


def on_key_up(_window, keycode, *_rest):
    key_name = keyboard_mapping.get(keycode)
    if key_name:
        controls[key_name] = False


def on_key_down(_window, keycode, *_rest):
    key_name = keyboard_mapping.get(keycode)
    if key_name:
        controls[key_name] = True


controls = {k: False for k in
            ['w', 's', 'a', 'tab', 'd', 'space', 'dash', 'y', 'b', 'menu', 'start', 'map', 'x']}
