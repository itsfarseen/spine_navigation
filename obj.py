import numpy as np
import OpenGL.GL as gl
import glm
import ctypes
from collections import namedtuple
from pathlib import Path

Material = namedtuple("Material", ["Ns", "Ka", "Kd", "Ks", "Ke", "Ni", "d", "illum"])


class ObjMesh:
    def __init__(self, filename, shader):
        self._load_obj(filename)
        self.shader = shader
        self.position = glm.vec3(0, 0, 0)
        self.rotationX = 0
        self.rotationY = 0
        self.rotationZ = 0
        self.rotationMat = None

    def _load_mtl(self, objfilename, mtlfilename):
        objpath = Path(objfilename)
        mtlpath = objpath.parent / mtlfilename

        mtls = []
        mtlsIdx = {}

        with open(mtlpath, "r") as file:
            hasMtl = False
            name = Ns = Ka = Kd = Ks = Ke = Ni = d = illum = None

            for line in file.readlines():
                if line.startswith("newmtl "):
                    if hasMtl:
                        mtl = Material(Ns, Ka, Kd, Ks, Ke, Ni, d, illum)
                        mtls.append(mtl)
                        mtlsIdx[name] = len(mtls) - 1
                    name = line.split()[1]
                    hasMtl = True
                elif line.startswith("Ns "):
                    Ns = float(line.split()[1])
                elif line.startswith("Ka"):
                    line = line.split()[1:]
                    Ka = (float(line[0]), float(line[1]), float(line[2]))
                elif line.startswith("Kd"):
                    line = line.split()[1:]
                    Kd = (float(line[0]), float(line[1]), float(line[2]))
                elif line.startswith("Ks"):
                    line = line.split()[1:]
                    Ks = (float(line[0]), float(line[1]), float(line[2]))
                elif line.startswith("Ke"):
                    line = line.split()[1:]
                    Ke = (float(line[0]), float(line[1]), float(line[2]))
                elif line.startswith("Ni "):
                    Ni = float(line.split()[1])
                elif line.startswith("d "):
                    d = float(line.split()[1])
                elif line.startswith("illum "):
                    illum = int(line.split()[1])
            if hasMtl:
                mtl = Material(Ns, Ka, Kd, Ks, Ke, Ni, d, illum)
                mtls.append(mtl)
                mtlsIdx[name] = len(mtls) - 1
        self.materials = mtls
        self.materialsIdx = mtlsIdx

    def _load_obj(self, filename):
        vertices = []
        tex = []
        normals = []

        vertices_combined = []
        faces_combined = []
        with open(filename, "r") as file:
            curMtl = None
            for i, line in enumerate(file.readlines()):
                if line.startswith("mtllib "):
                    mtlfilename = line.split()[1]
                    self._load_mtl(objfilename=filename, mtlfilename=mtlfilename)
                elif line.startswith("usemtl "):
                    curMtl = self.materialsIdx[line.split()[1]]
                elif line.startswith("o "):
                    continue
                elif line.startswith("v "):
                    line = line.split()[1:]
                    v = (float(line[0]), float(line[1]), float(line[2]))
                    vertices.append(v)
                elif line.startswith("vt "):
                    line = line.split()[1:]
                    t = (float(line[0]), float(line[1]))
                    tex.append(t)
                elif line.startswith("vn "):
                    line = line.split()[1:]
                    n = (float(line[0]), float(line[1]), float(line[2]))
                    normals.append(n)
                elif line.startswith("f "):
                    line = line.split()[1:]
                    if len(line) == 3:
                        faces = [(line[0], line[1], line[2])]
                    elif len(line) == 4:
                        faces = [
                            (line[0], line[1], line[2]),
                            (line[0], line[2], line[3]),
                        ]
                    else:
                        raise ValueError(
                            "Face with more than 4 edges not supported",
                            i + 1,
                            line,
                            len(line),
                        )
                    for face in faces:
                        face_combined = []
                        for vertex in face:
                            vertex = vertex.split("/")
                            v = vertices[int(vertex[0]) - 1]
                            vt = tex[int(vertex[1]) - 1]
                            vn = normals[int(vertex[2]) - 1]
                            v_combined = (v, vt, vn, curMtl)

                            # try:
                            #     i = vertices_combined.index(v_combined)
                            # except ValueError:
                            vertices_combined.append(v_combined)
                            i = len(vertices_combined) - 1
                            face_combined.append(i)
                        faces_combined.append(tuple(face_combined))

        vertices_dtype = np.dtype(
            [
                (
                    "pos",
                    [
                        ("x", np.float32),
                        ("y", np.float32),
                        ("z", np.float32),
                    ],
                ),
                (
                    "uv",
                    [
                        ("u", np.float32),
                        ("v", np.float32),
                    ],
                ),
                (
                    "n",
                    [
                        ("x", np.float32),
                        ("y", np.float32),
                        ("z", np.float32),
                    ],
                ),
                ("mtl", np.int32),
            ]
        )
        self.vertices = np.array(vertices_combined, dtype=vertices_dtype)
        self.faces = np.array(faces_combined, dtype=(np.uint32, 3))

    def uploadMeshData(self):
        # create VBO, upload data
        vbo = gl.glGenBuffers(1)  # type: ignore
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
        vbo_data = self.vertices
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER, vbo_data.nbytes, vbo_data, gl.GL_DYNAMIC_DRAW
        )

        # create EBO, upload data
        ebo = gl.glGenBuffers(1)  # type: ignore
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, ebo)
        ebo_data = self.faces
        gl.glBufferData(
            gl.GL_ELEMENT_ARRAY_BUFFER,
            ebo_data.nbytes,
            ebo_data,
            gl.GL_DYNAMIC_DRAW,
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
        loc = self.shader.getUVAttribLoc()
        gl.glEnableVertexArrayAttrib(vao, loc)
        gl.glVertexAttribPointer(
            loc,
            2,
            gl.GL_FLOAT,
            False,
            vbo_data.strides[0],
            ctypes.c_void_p(3 * 4),
        )
        loc = self.shader.getNormalAttribLoc()
        gl.glEnableVertexArrayAttrib(vao, loc)
        gl.glVertexAttribPointer(
            loc,
            3,
            gl.GL_FLOAT,
            False,
            vbo_data.strides[0],
            ctypes.c_void_p(5 * 4),
        )
        loc = self.shader.getMaterialAttribLoc()
        gl.glEnableVertexArrayAttrib(vao, loc)
        gl.glVertexAttribIPointer(
            loc,
            1,
            gl.GL_INT,
            vbo_data.strides[0],
            ctypes.c_void_p(8 * 4),
        )  # type: ignore

        # attach EBO to VAO
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, ebo)

        self.vao = vao
        gl.glBindVertexArray(0)

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
        self.shader.setMaterials(self.materials)
        matT = self.getTranslationMat()
        matR = self.getRotationMat()
        modelMat = matT * matR
        self.shader.setModelMatrix(modelMat)

        gl.glBindVertexArray(self.vao)
        gl.glDrawElements(
            gl.GL_TRIANGLES,
            len(self.faces) * 3,
            gl.GL_UNSIGNED_INT,
            ctypes.c_void_p(0),
        )  # type: ignore
        gl.glBindVertexArray(0)
