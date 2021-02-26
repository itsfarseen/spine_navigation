from shader import Shader

class SimpleShader(Shader):
    def __init__(self):
        vertexCode = """#version 330 core
        uniform mat4 camera;
        in vec3 position;
        in vec3 color;

        out vec3 f_color;

        void main() {
            f_color = color;
            gl_Position = camera*vec4(position, 1.0);
        }
        """

        fragmentCode = """#version 330 core
        in vec3 f_color;
        void main() {
            gl_FragColor = vec4(f_color, 1.0);
        }
        """
        super().__init__(vertexCode, fragmentCode)
