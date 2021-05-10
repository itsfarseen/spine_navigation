from shader import Shader
import OpenGL.GL as gl
import glm


class VolumeShader(Shader):
    def __init__(self):
        vertexCode = """#version 330 core
        uniform mat4 model, view, rot, projection = mat4(1.0);

        in vec3 position;
        out vec3 f_pos;

        void main() {
            vec4 origin = view*vec4(0.0,0.0,0.0, 1.0);
            
            vec4 rv = rot*vec4(position, 1.0); 
            f_pos = rv.xyz;

            gl_Position = projection*(origin + model*vec4(position, 1.0));
        }
        """

        fragmentCode = """#version 330 core
        
        uniform sampler3D tex;

        in vec3 f_pos;
        
        void main() {
            float col = 0.0;
            col += texture(tex, (f_pos+10.0)/32.0).x;

            gl_FragColor = vec4(col,0.0,0.0,col*0.4+0.0005);
        }
        """
        super().__init__(vertexCode, fragmentCode)

    def compile(self):
        super().compile()
        # some drivers don't respect default uniform values set in shader
        self.setModelMatrix(glm.identity(glm.mat4))

    def setModelMatrix(self, mat4):
        self._setMat4("model", mat4)

    def setViewMatrix2(self, view, rot):
        self._setMat4("view", view)
        self._setMat4("rot", rot)

    def setProjectionMatrix(self, mat4):
        self._setMat4("projection", mat4)

    def setTexIdx(self, i):
        self._setInt("tex", i)

    def getPositionAttribLoc(self):
        return self._getAttribLocation("position")
