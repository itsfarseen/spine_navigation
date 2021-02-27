from shader import Shader
import OpenGL.GL as gl
import glm


class ObjShader(Shader):
    def __init__(self):
        vertexCode = """#version 330 core
        uniform mat4 camera;
        in vec3 position;
        in vec2 uv_coord;
        in vec3 normal;

        out vec2 f_uv;
        out vec3 f_normal;

        void main() {
            f_uv = uv_coord;
            f_normal = normal;

            gl_Position = camera*vec4(position, 1.0);
        }
        """

        fragmentCode = """#version 330 core
        in vec2 f_uv;
        in vec3 f_normal;

        vec3 x;
        void main() {
            x = 0.01*vec3(f_uv, 1.0) + 0.01*f_normal + vec3(0.0, 1.0, 0.0);
            gl_FragColor = vec4(x, 1.0);
        }
        """
        super().__init__(vertexCode, fragmentCode)

    def setCameraMatrix(self, cameraMat4):
        self.use()
        loc = self._getUniformLocation("camera")
        gl.glUniformMatrix4fv(loc, 1, False, glm.value_ptr(cameraMat4))  # type: ignore

    def getPositionAttribLoc(self):
        return self._getAttribLocation("position")

    def getUVAttribLoc(self):
        a = self._getAttribLocation("uv_coord")
        assert a != -1
        return a

    def getNormalAttribLoc(self):
        return self._getAttribLocation("normal")
