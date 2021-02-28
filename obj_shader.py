from shader import Shader
import OpenGL.GL as gl
import glm


class ObjShader(Shader):
    def __init__(self):
        vertexCode = """#version 330 core
        uniform mat4 model, view, projection = mat4(1.0);

        in vec3 position;
        in vec2 uv_coord;
        in vec3 normal;
        in int material;

        out vec2 f_uv;
        out vec3 f_normal;
        out vec3 f_pos;
        flat out int f_material;

        void main() {
            f_uv = uv_coord;
            f_normal = normal;
            f_pos = position;
            f_material = material;

            gl_Position = projection*view*model*vec4(position, 1.0);
        }
        """

        fragmentCode = """#version 330 core
        float ambientStrength = 0.2;

        struct Material {
            float Ns;
            vec3 Ka;
            vec3 Kd;
            vec3 Ks;
        };
        uniform Material[5] materials;

        uniform int renderMaterialOnly = -1;

        in vec2 f_uv;
        in vec3 f_normal;
        in vec3 f_pos;
        flat in int f_material;

        vec3 light = vec3(10.0, 10.0, 10.0);
        vec3 lightColor = vec3(1.0, 1.0, 1.0);

        Material material = materials[f_material];

        // to prevent optimizing out of attributes
        vec3 x = 0.001*vec3(f_uv, 1.0);

        void main() {
            if(renderMaterialOnly >= 0) {
                if(renderMaterialOnly == f_material) {
                    gl_FragColor = vec4(1.0, 1.0, 1.0, 1.0);
                } else {
                    gl_FragColor = vec4(1.0, 1.0, 1.0, 0.0);
                }
                return;
            }

            vec3 norm = normalize(f_normal);
            vec3 lightDir = normalize(light - f_pos);
            float diff = max(dot(norm, lightDir), 0.0);
            vec3 diffuse = diff * lightColor;

            vec3 ambient = ambientStrength * material.Ka;

            vec3 shade = (ambient + diffuse) * material.Kd + x;

            gl_FragColor = vec4(shade, 1.0);
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

    def getPositionAttribLoc(self):
        return self._getAttribLocation("position")

    def getUVAttribLoc(self):
        return self._getAttribLocation("uv_coord")

    def getNormalAttribLoc(self):
        return self._getAttribLocation("normal")

    def getMaterialAttribLoc(self):
        return self._getAttribLocation("material")

    def setMaterials(self, materials):
        for i, material in enumerate(materials):
            matUni = "materials[{}]".format(i)
            self._setFloat(matUni + ".Ns", material.Ns)
            self._setVec3(matUni + ".Ka", material.Ka)
            self._setVec3(matUni + ".Kd", material.Kd)
            self._setVec3(matUni + ".Ks", material.Ks)

    def renderMaterialOnly(self, materialIdx):
        self._setInt("renderMaterialOnly", materialIdx)
