import OpenGL.GL as gl
from shader import Shader
import glm


class GridShader(Shader):
    def __init__(self):
        vertexCode = """#version 330 core
        uniform mat4 camera;
        in vec3 position;

        out vec3 f_coord;
        out float f_z;

        void main() {
            f_coord = position;
            gl_Position = camera*vec4(position, 1.0);
            f_z = gl_Position.z;
        }
        """

        fragmentCode = """#version 330 core
        in vec3 f_coord;
        in float f_z;

        float line_width = 0.01;
        float alpha;
        vec3 f_coord1;
        void main() {
            alpha = max(0.0, min(1.0, 4.0/f_z));
            f_coord1 = f_coord;
            if(abs(f_coord1.z) <= line_width) {
                gl_FragColor = vec4(0.5, 0.1, 0.1, alpha);
            } else if(abs(f_coord1.x) <= line_width) {
                gl_FragColor = vec4(0.1, 0.1, 0.5, alpha);
            } else if(fract(f_coord1.x) <= line_width || fract(f_coord1.z) <= line_width) {
                gl_FragColor = vec4(0.5, 0.5, 0.5, alpha);
            } else {
                gl_FragColor = vec4(0.2, 0.2, 0.2, 0.0);
            }
        }
        """
        super().__init__(vertexCode, fragmentCode)

    def setCameraMatrix(self, cameraMat4):
        self.use()
        loc = self._getUniformLocation("camera")
        gl.glUniformMatrix4fv(loc, 1, False, glm.value_ptr(cameraMat4))  # type: ignore

    def getPositionAttribLoc(self):
        return self._getAttribLocation("position")
