import OpenGL.GL as gl
import nibabel as nib
import glm
import numpy as np
import ctypes
import matplotlib.pyplot as plt
from voxels import sphere
import pywavefront
from shader import Shader
from window import Window
from cube import CubeMesh
from camera import Camera
import logging
import glfw


def setup():
    gl.glViewport(0, 0, window.width(), window.height())
    gl.glEnable(gl.GL_BLEND)
    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)


def display():
    gl.glClearColor(0.3, 0.4, 0.38, 1.0)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)

    shader.use()
    camera.update()
    cube.draw()


last_x = None
last_y = None
move = False


def mouse(btn, action, mods, x, y):
    global last_x, last_y, move
    if action == glfw.PRESS:
        last_x = None
        last_y = None
        move = mods == glfw.MOD_SHIFT
        return

    if (
        last_x is not None
        and last_y is not None
        and x is not None
        and y is not None
    ):
        delta_x = x - last_x
        delta_y = y - last_y
        camera.move(delta_x, delta_y)
    last_x = x
    last_y = y


shader = Shader()
cube = CubeMesh()
window = Window(display, mousefn=mouse)
camera = Camera()


def main():
    window.setup()
    shader.setup()
    cube.setup(shader)
    camera.setup(shader, window)

    setup()
    window.run()


if __name__ == "__main__":
    main()
