import OpenGL.GL as gl
import numpy as np
import ctypes


class FrameMesh:
    width = 0.005
    vertices = [
        (0 - width, 1, 0),
        (0 + width, 1, 0),
        (0 - width, -1, 0),
        (0 + width, -1, 0),
        (1, 0 - width, 0),
        (1, 0 + width, 0),
        (-1, 0 - width, 0),
        (-1, 0 + width, 0),
    ]

    faces = [
        (0, 1, 2),
        (1, 2, 3),
        (0 + 4, 1 + 4, 2 + 4),
        (1 + 4, 2 + 4, 3 + 4),
    ]

    def __init__(self, shader):
        self.shader = shader

    def uploadMeshData(self):
        vbo = gl.glGenBuffers(1)  # type: ignore
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
        vbo_data = np.array(self.vertices, dtype=(np.float32, 3))
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER, vbo_data.nbytes, vbo_data, gl.GL_STATIC_DRAW
        )

        # create EBO, upload data
        ebo = gl.glGenBuffers(1)  # type: ignore
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, ebo)
        ebo_data = np.array(self.faces, dtype=(np.uint32, 3))
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
        positionLoc = self.shader.getPositionAttribLoc()
        gl.glEnableVertexArrayAttrib(vao, positionLoc)
        gl.glVertexAttribPointer(
            positionLoc,
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
