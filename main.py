# vi: foldmethod=indent:
import OpenGL.GL as gl
import OpenGL.GLUT as glut
import nibabel as nib
import glm
import numpy as np
import ctypes
import matplotlib.pyplot as plt
from voxels import sphere
import pywavefront

window = None

WIN_WIDTH = 480
WIN_HEIGHT = 480
WIN_ASPECT = WIN_WIDTH / WIN_HEIGHT


def setup():
    gl.glViewport(0, 0, WIN_WIDTH, WIN_HEIGHT)
    gl.glEnable(gl.GL_BLEND)
    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)


def display():
    gl.glClearColor(0.3, 0.4, 0.38, 1.0)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)

    glut.glutSwapBuffers()


def reshape(width, height):
    glut.glutReshapeWindow(WIN_WIDTH, WIN_HEIGHT)


def keyboard(key, x, y):
    if key in (b'q',):
        glut.glutLeaveMainLoop()
        return
    glut.glutPostRedisplay()


def mouse(btn, state, x, y):
    if state == glut.GLUT_UP:
        # process only button press and not release
        # (scroll wheel movements are interpreted as button presses)
        return
    glut.glutPostRedisplay()


def setupWindow():
    global window
    glut.glutInit()
    glut.glutInitContextVersion(3, 3)
    glut.glutInitContextProfile(glut.GLUT_CORE_PROFILE)
    glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGBA)  # type: ignore
    window = glut.glutCreateWindow("Hello World [Float]")
    glut.glutReshapeFunc(reshape)
    glut.glutDisplayFunc(display)
    glut.glutMouseFunc(mouse)
    glut.glutKeyboardFunc(keyboard)


program = None


def setupShaders():
    vertexCode = """#version 330 core
    in vec3 position;

    void main() {
        gl_Position = vec4(position, 1.0);
    }
    """

    fragmentCode = """#version 330 core
    void main() {
        gl_FragColor = vec4(1.0, 1.0, 1.0, 1.0);
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


def main():
    setupWindow()
    setupShaders()
    setup()
    glut.glutMainLoop()


if __name__ == "__main__":
    main()
