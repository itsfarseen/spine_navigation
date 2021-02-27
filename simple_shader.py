from shader import Shader
import OpenGL.GL as gl
import glm


class SimpleShader(Shader):
    def __init__(self):
        vertexCode = """#version 330 core
        uniform mat4 model, view, projection = mat4(1.0);

        in vec3 position;
        in vec3 color;

        out vec3 f_color;

        void main() {
            f_color = color;
            gl_Position = projection*view*model*vec4(position, 1.0);
        }
        """

        fragmentCode = """#version 330 core
        in vec3 f_color;
        void main() {
            gl_FragColor = vec4(f_color, 1.0);
        }
        """
        super().__init__(vertexCode, fragmentCode)

    def setModelMatrix(self, mat4):
        self._setMat4("model", mat4)

    def setViewMatrix(self, mat4):
        self._setMat4("view", mat4)

    def setProjectionMatrix(self, mat4):
        self._setMat4("projection", mat4)

    def getPositionAttribLoc(self):
        return self._getAttribLocation("position")

    def getColorAttribLoc(self):
        return self._getAttribLocation("color")
