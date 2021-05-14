import OpenGL.GL as gl
from shader import Shader
import glm


class FrameShader(Shader):
    def __init__(self):
        vertexCode = """#version 330 core
        in vec3 position;
        out vec3 fpos;

        void main() {
            fpos = position;
            gl_Position = vec4(position.xy, -1.0, 1.0);
        }
        """

        fragmentCode = """#version 330 core
        in vec3 fpos;

        void main() {
            gl_FragColor = vec4(0, 0, 0, 1);
        }
        """
        super().__init__(vertexCode, fragmentCode)

    # def setViewMatrix(self, mat4):
    #     pass

    # def setProjectionMatrix(self, mat4):
    #     pass

    def getPositionAttribLoc(self):
        return self._getAttribLocation("position")
