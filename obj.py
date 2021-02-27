import numpy as np
import OpenGL.GL as gl
import glm
import ctypes


class ObjMesh:
    def __init__(self, filename, shader):
        self._load_obj(filename)
        self.shader = shader

    def _load_obj(self, filename):
        vertices = []
        tex = []
        normals = []

        vertices_combined = []
        faces_combined = []
        with open(filename, "r") as file:
            for line in file.readlines():
                if line.startswith("o "):
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
                            len(line),
                        )
                    for face in faces:
                        face_combined = []
                        for vertex in face:
                            vertex = vertex.split("/")
                            v = vertices[int(vertex[0]) - 1]
                            vt = tex[int(vertex[1]) - 1]
                            vn = normals[int(vertex[2]) - 1]
                            v_combined = (v, vt, vn)

                            try:
                                i = vertices_combined.index(v_combined)
                            except ValueError:
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
            ]
        )
        self.vertices = np.array(vertices_combined, dtype=vertices_dtype)
        self.faces = np.array(faces_combined, dtype=(np.uint32, 3))

    def setup(self):
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

        # attach EBO to VAO
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, ebo)

        self.vao = vao
        gl.glBindVertexArray(0)

    def draw(self):
        self.shader.use()
        gl.glBindVertexArray(self.vao)
        gl.glDrawElements(
            gl.GL_TRIANGLES,
            len(self.faces) * 3,
            gl.GL_UNSIGNED_INT,
            ctypes.c_void_p(0),
        )  # type: ignore
        gl.glBindVertexArray(0)
