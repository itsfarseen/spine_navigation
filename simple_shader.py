from shader import Shader
import OpenGL.GL as gl
import glm


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

    def setCameraMatrix(self, cameraMat4):
        self.use()
        loc = self._getUniformLocation("camera")
        gl.glUniformMatrix4fv(loc, 1, False, glm.value_ptr(cameraMat4))  # type: ignore

    def getPositionAttribLoc(self):
        return self._getAttribLocation("position")

    def getColorAttribLoc(self):
        return self._getAttribLocation("color")
