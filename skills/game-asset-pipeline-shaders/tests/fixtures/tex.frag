#version 310 es
precision mediump float;
uniform sampler2D u_tex;
out vec4 o_color;
void main() { o_color = texture(u_tex, vec2(0.5)); }
