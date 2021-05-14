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
            vec4 origin = vec4(0.0,0.0,0.0, 1.0);
            
            f_pos = position;            
            gl_Position = projection*view*model*rot*(origin + vec4(position, 1.0));
            // gl_Position = projection*view*model*vec4(position, 1.0);
        }
        """

        fragmentCode = """#version 330 core

        uniform mat4 rot, persp, projection, model, view;        
        uniform sampler3D tex;
        uniform float xMax, yMax, zMax;
        uniform float xMax2, yMax2, zMax2;

        in vec3 f_pos;

        float f(float x, float xMin, float xMax, float yMin, float yMax) {
            // axMin + b = yMin
            // axMax + b = yMax
            // a(xMin - xMax) = yMin - yMax
            float a = (yMax - yMin)/(xMax - xMin);
            float b = yMin - a*xMin;
            return a*x + b;
        }

        float g(float x, float xMax, float xMax2) {
            float a = f(x, -1, 1, 0, xMax);
            return f(a, 0, xMax2, 0, 1);
        }

        float pf_adjust(float x, float pf) {
            return (x-0.5)*pf + 0.5;
        }

        void main() {
            float col = 0;
            float alpha = 0;
            vec4 origin = vec4(0.0,0.0,0.0, 1.0);
            vec4 ff = projection*view*model*rot*(origin + vec4(f_pos, 1.0));
            gl_FragDepth = (1 + ff.z/ff.w)/2;

            for(float zz = -1.0; zz <= 1.0; zz += 0.1) {
                vec4 rv = persp*rot*vec4(f_pos.xy, zz, 1.0); 
                //rv.x *= rv.w;
                //rv.y *= rv.w;
                float pf = f(zz, 0, 1, 1.0, 0.9);

                float x = pf_adjust(g(rv.x, xMax, xMax2), pf);
                float y = pf_adjust(g(rv.y, yMax, yMax2), pf);
                float z = g(rv.z, zMax, zMax2);
                vec3 texCoord = vec3(x,y,z);
                
                float hu = texture(tex, texCoord).x/1000;

                if(col < 0.01 && hu > 0.01) {
                    alpha = 0.9;
                    vec4 ff = projection*view*model*rot*(origin + vec4(f_pos.xy, zz, 1.0));
                    gl_FragDepth = (1 + ff.z/ff.w)/2;
                }
                col = max(col, hu);
             
            }
            gl_FragColor = vec4(col,col,col,alpha);
        }
        """
        super().__init__(vertexCode, fragmentCode)

    def compile(self):
        super().compile()
        # some drivers don't respect default uniform values set in shader
        self.setModelMatrix(glm.identity(glm.mat4))

    def setModelMatrix(self, mat4):
        self._setMat4("model", mat4)

    def setViewMatrix2(self, view, rot, persp):
        self._setMat4("view", view)
        self._setMat4("rot", rot)
        self._setMat4("persp", persp)

    def setProjectionMatrix(self, mat4):
        self._setMat4("projection", mat4)

    def setTexIdx(self, i):
        self._setInt("tex", i)

    def setDims(self, xMax, yMax, zMax, xMax2, yMax2, zMax2):
        self._setFloat("xMax", xMax)
        self._setFloat("yMax", yMax)
        self._setFloat("zMax", zMax)
        self._setFloat("xMax2", xMax2)
        self._setFloat("yMax2", yMax2)
        self._setFloat("zMax2", zMax2)

    def getPositionAttribLoc(self):
        return self._getAttribLocation("position")
