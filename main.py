from obj_shader import ObjShader
from obj import ObjMesh
import OpenGL.GL as gl
import nibabel as nib
import glm
import numpy as np
import ctypes
import matplotlib.pyplot as plt
from voxels import sphere
import pywavefront
from simple_shader import SimpleShader
from window import Window
from cube import CubeMesh
from camera import Camera
from grid_shader import GridShader
from grid import GridMesh
import logging
import glfw


class App:
    def __init__(self):
        self.window = Window(self.display)
        self.window.setupContext()
        self.window.addKeyboardHandler(self.keyboard)

        self.grid_shader = GridShader()
        self.grid_shader.compile()
        self.grid = GridMesh(self.grid_shader)
        self.grid.uploadMeshData()

        self.obj_shader = ObjShader()
        self.obj_shader.compile()
        self.operating_table_obj = ObjMesh(
            "./assets/OperatingTable.obj", self.obj_shader
        )
        self.operating_table_obj.uploadMeshData()
        self.instrument_obj = ObjMesh(
            "./assets/instrument1.obj", self.obj_shader
        )
        self.instrument_obj.uploadMeshData()

        self.camera = Camera(self.window, [self.grid_shader, self.obj_shader])
        self.camera.setAllUniforms()

        self.cameraControls = CameraControls(self.camera)
        self.cameraControls.setupHandlers(self.window)

        self.renderGleonsOnly = False

        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_FRAMEBUFFER_SRGB)

    def display(self):
        gl.glViewport(0, 0, self.window.width(), self.window.height())
        if self.renderGleonsOnly:
            gl.glClearColor(0.0, 0.0, 0.0, 1.0)
            self.obj_shader.renderMaterialOnly(1)
            objectsToDraw = [self.instrument_obj]
        else:
            gl.glClearColor(0.3, 0.4, 0.38, 1.0)
            self.obj_shader.renderMaterialOnly(-1)
            objectsToDraw = [
                self.instrument_obj,
                self.operating_table_obj,
                self.grid,
            ]

        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)  # type: ignore
        for obj in objectsToDraw:
            obj.draw()

    def keyboard(self, key, action, mods):
        if key == glfw.KEY_TAB and action == glfw.PRESS:
            self.renderGleonsOnly = not self.renderGleonsOnly

    def run(self):
        self.window.run()


class CameraControls:
    def __init__(self, camera):
        self.camera = camera

        self.last_x = None
        self.last_y = None
        self.mode = None

    def setupHandlers(self, window):
        window.addScrollHandler(self.scroll)
        window.addMouseHandler(self.mouse)

    def scroll(self, x, y):
        self.camera.zoom(y)
        return Window.EVENT_CONSUMED

    def mouse(self, btn, action, mods, warp, x, y):
        if action == glfw.PRESS and btn == glfw.MOUSE_BUTTON_3:
            if mods == glfw.MOD_SHIFT:
                self.mode = "MOVE"
            else:
                self.mode = "ROTATE"
            self.last_x = x
            self.last_y = y
            return Window.EVENT_CONSUMED

        if action == glfw.RELEASE and self.mode is not None:
            self.mode = None
            self.last_x = x
            self.last_y = y
            return Window.EVENT_CONSUMED

        if (
            self.last_x is not None
            and self.last_y is not None
            and x is not None
            and y is not None
            and self.mode is not None
            and not warp
        ):
            delta_x = x - self.last_x
            delta_y = y - self.last_y
            if self.mode == "MOVE":
                self.camera.move(delta_x, delta_y)
            elif self.mode == "ROTATE":
                self.camera.rotate(delta_x, delta_y)
            else:
                raise ValueError("undefined mode", self.mode)
            self.last_x = x
            self.last_y = y
            return Window.EVENT_CONSUMED

        self.last_x = x
        self.last_y = y


if __name__ == "__main__":
    app = App()
    app.run()
