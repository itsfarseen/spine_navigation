import OpenGL.GL as gl
import numpy as np
import ctypes


class CubeMesh:
    vertices = [
        # Front
        (0.5, 0.5, 0.5, 1.0, 0.0, 0.0),  # red
        (-0.5, 0.5, 0.5, 0.0, 1.0, 0.0),  # green
        (-0.5, -0.5, 0.5, 0.0, 0.0, 1.0),  # blue
        (0.5, -0.5, 0.5, 0.0, 0.0, 0.0),  # black
        # Back
        (0.5, 0.5, -0.5, 1.0, 1.0, 0.0),  # yellow
        (-0.5, 0.5, -0.5, 1.0, 0.0, 1.0),  # violet
        (-0.5, -0.5, -0.5, 0.0, 1.0, 1.0),  # cyan
        (0.5, -0.5, -0.5, 0.5, 0.5, 0.5),  # grey
    ]

    faces = [
        # Front
        (0, 1, 3),
        (1, 2, 3),
        # Bottom
        (3, 2, 7),
        (2, 6, 7),
        # Back
        (7, 6, 4),
        (5, 6, 4),
        # Top
        (4, 5, 0),
        (5, 1, 0),
        # Left
        (2, 1, 6),
        (1, 5, 6),
        # Right
        (0, 3, 4),
        (3, 7, 4),
    ]

    def __init__(self, shader):
        self.shader = shader

    def setup(self):
        # create VBO, upload data
        vbo = gl.glGenBuffers(1)  # type: ignore
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
        vbo_data = np.array(self.vertices, dtype=(np.float32, 6))
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER, vbo_data.nbytes, vbo_data, gl.GL_DYNAMIC_DRAW
        )

        # create EBO, upload data
        ebo = gl.glGenBuffers(1)  # type: ignore
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, ebo)
        ebo_data = np.array(self.faces, dtype=(np.uint32, 3))
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
        colorLoc = self.shader.getColorAttribLoc()
        gl.glEnableVertexArrayAttrib(vao, colorLoc)
        gl.glVertexAttribPointer(
            colorLoc,
            3,
            gl.GL_FLOAT,
            False,
            vbo_data.strides[0],
            ctypes.c_void_p(3 * 4),
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
            len(self.faces * 3),
            gl.GL_UNSIGNED_INT,
            ctypes.c_void_p(0),
        )  # type: ignore
        gl.glBindVertexArray(0)
