uniform float x;
//float collides(float x) {
//    return 1;
//}

// Kivy uses this effect function for the effect widget's shader.
vec4 effect(vec4 frag_color, sampler2D texture0, vec2 tex_coords0, vec2 coords) {
    // coords are relative to the widget.
    if (x > 700.0) {
        return vec4(0, 1, 1, 1);
    }
    else {
        return vec4(1, 0, 0, 1);
    }
}