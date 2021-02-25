import OpenGL.GL as gl
import OpenGL.GLUT as glut
import nibabel as nib
import glm
import numpy as np
import ctypes
import matplotlib.pyplot as plt
from voxels import sphere
import pywavefront
from shader import Shader
from window import Window


def setup():
    gl.glViewport(0, 0, window.width(), window.height())
    gl.glEnable(gl.GL_BLEND)
    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)


def display():
    gl.glClearColor(0.3, 0.4, 0.38, 1.0)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)

    shader.use()

    glut.glutSwapBuffers()


shader = Shader()
window = Window(display)


def main():
    window.setup()
    shader.setup()

    setup()
    window.run()


if __name__ == "__main__":
    main()
