import OpenGL.GL as gl
import numpy as np
import ctypes


class CubeMesh:
    vertices = [
        (-0.5, 0.5, 0.5),
        (0.5, 0.5, 0.5),
        (0.5, -0.5, 0.5),
        (-0.5, -0.5, 0.5),
        (-0.5, 0.5, -0.5),
        (0.5, 0.5, -0.5),
        (0.5, -0.5, -0.5),
        (-0.5, -0.5, -0.5),
    ]

    faces = [
        # Top
        (1, 0, 2),
        (3, 2, 0),
        # Front
        (2, 3, 6),
        (7, 6, 3),
        # Bottom
        (6, 7, 5),
        (4, 5, 7),
        # Back
        (5, 4, 1),
        (0, 1, 4),
        # Left
        (3, 0, 7),
        (4, 7, 0),
        # Right
        (1, 2, 3),
        (6, 3, 2),
    ]

    def __init__(self):
        pass

    def setup(self, shader):
        # create VBO, upload data
        vbo = gl.glGenBuffers(1)  # type: ignore
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
        vbo_data = np.array(self.vertices, dtype="f4, f4, f4")
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER, vbo_data.nbytes, vbo_data, gl.GL_DYNAMIC_DRAW
        )

        # create EBO, upload data
        ebo = gl.glGenBuffers(1)  # type: ignore
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, ebo)
        ebo_data = np.array(self.faces, dtype="B, B, B")
        gl.glBufferData(
            gl.GL_ELEMENT_ARRAY_BUFFER,
            ebo_data.nbytes,
            ebo_data,
            gl.GL_DYNAMIC_DRAW,
        )

        # create VAO
        vao = gl.glGenVertexArrays(1)  # type: ignore
        gl.glBindVertexArray(vao)

        # specify position attribute of VBO thus attaching VBO to VAO
        loc = shader.getAttribLocation("position")
        gl.glEnableVertexArrayAttrib(vao, loc)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
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

    def draw(self):
        gl.glBindVertexArray(self.vao)
        gl.glDrawElements(
            gl.GL_TRIANGLES,
            len(self.faces),
            gl.GL_UNSIGNED_BYTE,
            ctypes.c_void_p(0),
        )  # type: ignore
