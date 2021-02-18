# vi: foldmethod=indent:
import OpenGL.GL as gl
import OpenGL.GLUT as glut
import nibabel as nib
import glm
import numpy as np
import ctypes

window = None

WIN_WIDTH = 960
WIN_HEIGHT = 480
WIN_ASPECT = WIN_WIDTH / WIN_HEIGHT


def setup():
    gl.glViewport(0, 0, WIN_WIDTH, WIN_HEIGHT)


def display():
    gl.glClearColor(0.3, 0.4, 0.38, 1.0)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)

    gl.glBindVertexArray(vao)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
    gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, ebo)
    offset = ctypes.c_void_p(0)
    gl.glDrawElements(gl.GL_TRIANGLES, 6, gl.GL_UNSIGNED_INT, offset)  # type: ignore

    # mat_proj = glm.perspective(45, WIN_ASPECT, 0.01, 1000.0)
    glut.glutSwapBuffers()


def reshape(width, height):
    glut.glutReshapeWindow(WIN_WIDTH, WIN_HEIGHT)


def keyboard(key, x, y):
    if key == b"\x1b":
        glut.glutLeaveMainLoop()


def setupWindow():
    global window
    glut.glutInit()
    glut.glutInitContextVersion(3, 3)
    glut.glutInitContextProfile(glut.GLUT_CORE_PROFILE)
    glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGBA)  # type: ignore
    window = glut.glutCreateWindow("Hello World [Float]")
    glut.glutReshapeFunc(reshape)
    glut.glutDisplayFunc(display)
    glut.glutKeyboardFunc(keyboard)


program = None


def setupShaders():
    vertexCode = """
    #version 330 core
    attribute vec2 position;
    void main() {
        gl_Position = vec4(position, 0.0, 1.0);
    }
    """

    fragmentCode = """
    #version 330 core
    void main() {
        gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);
    }
    """

    global program
    program = gl.glCreateProgram()
    vertex = gl.glCreateShader(gl.GL_VERTEX_SHADER)
    fragment = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)

    gl.glShaderSource(vertex, vertexCode)  # type: ignore
    gl.glShaderSource(fragment, fragmentCode)  # type: ignore

    gl.glCompileShader(vertex)
    if not gl.glGetShaderiv(vertex, gl.GL_COMPILE_STATUS):
        error = gl.glGetShaderInfoLog(vertex).decode()
        raise RuntimeError("vertex shader compilation error", error)

    gl.glCompileShader(fragment)
    if not gl.glGetShaderiv(fragment, gl.GL_COMPILE_STATUS):
        error = gl.glGetShaderInfoLog(fragment).decode()
        raise RuntimeError("fragment shader compilation error", error)

    gl.glAttachShader(program, vertex)
    gl.glAttachShader(program, fragment)
    gl.glLinkProgram(program)

    if not gl.glGetProgramiv(program, gl.GL_LINK_STATUS):  # type: ignore
        error = gl.glGetProgramInfoLog(program)
        raise RuntimeError("shader linking error", error)

    gl.glDetachShader(program, vertex)
    gl.glDetachShader(program, fragment)

    gl.glUseProgram(program)


vao = None
vbo = None
ebo = None

def setupModels():
    global vbo
    vbo = gl.glGenBuffers(1)  # type: ignore

    # upload data
    data = np.zeros((4, 2), dtype=np.float32)
    data[...] = (-0.5, 0.5), (0.5, 0.5), (0.5, -0.5), (-0.5, -0.5)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, data.nbytes, data, gl.GL_DYNAMIC_DRAW)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

    global vao
    vao = gl.glGenVertexArrays(1)  # type: ignore

    # configure attributes
    stride = data.strides[0]
    offset = ctypes.c_void_p(0)
    loc = gl.glGetAttribLocation(program, "position")

    gl.glBindVertexArray(vao)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
    gl.glEnableVertexAttribArray(loc)
    gl.glVertexAttribPointer(loc, 2, gl.GL_FLOAT, False, stride, offset)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
    gl.glBindVertexArray(0)

    global ebo
    ebo = gl.glGenBuffers(1) # type: ignore
    data = np.zeros((2, 3), dtype=np.uint32)
    data[...] = (0, 1, 2), (0, 2, 3)
    gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, ebo)
    gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, data.nbytes, data, gl.GL_DYNAMIC_DRAW)
    gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, 0)




def loadCt():
    img = nib.load("./ct/ct.nii.gz")


def main():
    setupWindow()
    setupShaders()
    setupModels()
    setup()
    glut.glutMainLoop()


if __name__ == "__main__":
    main()
