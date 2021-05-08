from shader import Shader
import OpenGL.GL as gl
import glm


class VolumeShader(Shader):
    def __init__(self):
        vertexCode = """#version 330 core
        uniform mat4 model, view, projection = mat4(1.0);

        in vec3 position;
        out vec3 f_pos;

        void main() {
            f_pos = position;

            gl_Position = projection*view*model*vec4(position, 1.0);
        }
        """

        fragmentCode = """#version 330 core
        
        uniform sampler3D tex;

        in vec3 f_pos;
        
        void main() {
            float col = 0.0;
            col += texture(tex, vec3((f_pos.xy+5.0)/16.0, 0.5)).x;
            
            gl_FragColor = vec4(col,0.0,0.0,col);
        }
        """
        super().__init__(vertexCode, fragmentCode)

    def compile(self):
        super().compile()
        # some drivers don't respect default uniform values set in shader
        self.setModelMatrix(glm.identity(glm.mat4))

    def setModelMatrix(self, mat4):
        self._setMat4("model", mat4)

    def setViewMatrix(self, mat4):
        self._setMat4("view", mat4)

    def setProjectionMatrix(self, mat4):
        self._setMat4("projection", mat4)

    def setTexIdx(self, i):
        self._setInt("tex", i)

    def getPositionAttribLoc(self):
        return self._getAttribLocation("position")
