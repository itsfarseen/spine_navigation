import numpy as np
import OpenGL.GL as gl
import glm
import ctypes
from collections import namedtuple
from pathlib import Path


class VolumeTestMesh:
    def __init__(self, shader):
        self.shader = shader
        self.position = glm.vec3(0, 0, 0)
        self.rotationX = 0
        self.rotationY = 0
        self.rotationZ = 0
        self.rotationMat = None
        self.xMax = self.yMax = self.zMax = 10

        self._generate_data()

    def _generate_data(self):
        vs = [(-2, 2, 0), (2, 2, 0), (2, -2, 0), (-2, -2, 0)]
        self.vertices = np.array(vs, dtype=np.float32)
        fs = [(0, 1, 3), (3, 1, 2), (4, 5, 7), (7, 5, 6)]
        self.faces = np.array(fs, dtype=(np.uint32))

        self.tex3d = np.zeros((16, 16, 16), dtype=np.uint8)

        for x in range(10):
            for y in range(10):
                for z in range(10):
                    if (
                        abs(
                            np.sqrt(
                                (2 * (x - 4.5)) ** 2 + (y - 4.5) ** 2 + (z - 4.5) ** 2
                            )
                            - 5
                        )
                        <= 1
                    ):
                        self.tex3d[x, y, z] = 255

    def uploadMeshData(self):
        # create VBO, upload data
        vbo = gl.glGenBuffers(1)  # type: ignore
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
        vbo_data = self.vertices
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER, vbo_data.nbytes, vbo_data, gl.GL_STATIC_DRAW
        )

        # create EBO, upload data
        ebo = gl.glGenBuffers(1)  # type: ignore
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, ebo)
        ebo_data = self.faces
        gl.glBufferData(
            gl.GL_ELEMENT_ARRAY_BUFFER,
            ebo_data.nbytes,
            ebo_data,
            gl.GL_STATIC_DRAW,
        )

        # create VAO
        vao = gl.glGenVertexArrays(1)  # type: ignore
        gl.glBindVertexArray(vao)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)

        # specify position attribute of VBO thus attaching VBO to VAO
        loc = self.shader.getPositionAttribLoc()
        gl.glEnableVertexArrayAttrib(vao, loc)
        gl.glVertexAttribPointer(
            loc,
            3,
            gl.GL_FLOAT,
            False,
            vbo_data.strides[0],
            ctypes.c_void_p(0),
        )

        # attach EBO to VAO
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, ebo)

        self.vao = vao
        gl.glBindVertexArray(0)

        # upload 3d texture
        self.texo = gl.glGenTextures(1)

        gl.glBindTexture(gl.GL_TEXTURE_3D, self.texo)
        gl.glTexParameteri(
            gl.GL_TEXTURE_3D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_BORDER
        )
        gl.glTexParameteri(
            gl.GL_TEXTURE_3D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_BORDER
        )
        gl.glTexParameteri(
            gl.GL_TEXTURE_3D, gl.GL_TEXTURE_WRAP_R, gl.GL_CLAMP_TO_BORDER
        )
        gl.glTexParameteri(gl.GL_TEXTURE_3D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
        gl.glTexParameteri(gl.GL_TEXTURE_3D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)

        gl.glTexImage3D(
            gl.GL_TEXTURE_3D,
            0,
            gl.GL_RGBA32F,
            16,
            16,
            16,
            0,
            gl.GL_RED,
            gl.GL_UNSIGNED_BYTE,
            self.tex3d,
        )
        gl.glBindTexture(gl.GL_TEXTURE_3D, 0)

    def moveTo(self, x, y, z):
        self.position = glm.vec3(x, y, z)

    def setRotationX(self, val):
        self.rotationX = val

    def setRotationY(self, val):
        self.rotationY = val

    def setRotationZ(self, val):
        self.rotationZ = val

    def getRotationMat(self):
        if self.rotationMat is None:
            mat = glm.identity(glm.mat4)
            mat = glm.rotate(mat, glm.radians(self.rotationX), glm.vec3(1, 0, 0))
            mat = glm.rotate(mat, glm.radians(self.rotationY), glm.vec3(0, 1, 0))
            mat = glm.rotate(mat, glm.radians(self.rotationZ), glm.vec3(0, 0, 1))
            return mat
        else:
            return self.rotationMat

    def getTranslationMat(self):
        mat = glm.identity(glm.mat4)
        mat = glm.translate(mat, self.position)
        return mat

    def draw(self):
        self.shader.use()
        matT = self.getTranslationMat()
        matR = self.getRotationMat()
        modelMat = matT * matR
        self.shader.setModelMatrix(modelMat)
        self.shader.setTexIdx(0)
        self.shader.setDims(self.xMax, self.yMax, self.zMax, 16, 16, 16)

        gl.glBindVertexArray(self.vao)
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_3D, self.texo)
        gl.glDrawElements(
            gl.GL_TRIANGLES,
            len(self.faces) * 3,
            gl.GL_UNSIGNED_INT,
            ctypes.c_void_p(0),
        )  # type: ignore
        gl.glBindVertexArray(0)
