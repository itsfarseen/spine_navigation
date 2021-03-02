from obj_shader import ObjShader
from obj import ObjMesh
import OpenGL.GL as gl
import glm
import numpy as np
import ctypes
import matplotlib.pyplot as plt
from voxels import sphere
from simple_shader import SimpleShader
from window import Window
from cube import CubeMesh
from camera import Camera
from grid_shader import GridShader
from grid import GridMesh
import logging
import glfw
from camera_controls import CameraControls
import multiprocessing.connection as mpc
import time
import threading
import imgui


class App:
    def __init__(self):
        self.listener = mpc.Listener(("127.0.0.1", 5001), "AF_INET")
        self.connection = None
        self.connectionThread = None
        self.acceptStreamConnectionInBackground()

        self.window = Window(self.display)
        # context has to be initialized before any function touches opengl
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
        self.instrument_pos = [0, 1.0, -0.2]
        self.instrument_obj.moveTo(*self.instrument_pos)

        self.stereoCamActive = False

        self.camera = Camera(self.window, [self.grid_shader, self.obj_shader])
        self.cameraControls = CameraControls(self.camera)
        self.cameraControls.installHandlers(self.window)

        self.stereoCamL = Camera(
            self.window, [self.grid_shader, self.obj_shader]
        )
        self.stereoCamR = Camera(
            self.window, [self.grid_shader, self.obj_shader]
        )

        self.stereoCamL.moveTo(0.29, 1.7128, -2)
        self.stereoCamR.moveTo(-0.29, 1.7128, -2)

        stereoCamPose = (0, -0.7, 1)
        self.stereoCamL.lookDir(*stereoCamPose)
        self.stereoCamR.lookDir(*stereoCamPose)

        self.renderGleonsOnly = False

        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_FRAMEBUFFER_SRGB)

        fb_zoom = 2
        self.fb_width = 480 * 2 * fb_zoom
        self.fb_height = 480 * fb_zoom

        self.rb = gl.glGenRenderbuffers(1)  # type: ignore
        gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, self.rb)
        gl.glRenderbufferStorage(
            gl.GL_RENDERBUFFER,
            gl.GL_RGB8,
            self.fb_width,
            self.fb_height,
        )
        gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, 0)

        self.fb = gl.glGenFramebuffers(1)  # type: ignore
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.fb)
        gl.glFramebufferRenderbuffer(
            gl.GL_FRAMEBUFFER,
            gl.GL_COLOR_ATTACHMENT0,
            gl.GL_RENDERBUFFER,
            self.rb,
        )
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

    def display(self):
        self.drawGleonsStereo()

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

        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        gl.glClear(gl.GL_DEPTH_BUFFER_BIT)

        if self.stereoCamActive:
            self.window.setWide(True)

            gl.glViewport(0, 0, self.window.width() // 2, self.window.height())
            self.stereoCamL.setAllUniforms()
            for obj in objectsToDraw:
                obj.draw()

            gl.glViewport(
                self.window.width() // 2,
                0,
                self.window.width() // 2,
                self.window.height(),
            )
            self.stereoCamR.setAllUniforms()
            for obj in objectsToDraw:
                obj.draw()
        else:
            self.window.setWide(False)

            gl.glViewport(0, 0, self.window.width(), self.window.height())
            self.camera.setAllUniforms()
            for obj in objectsToDraw:
                obj.draw()

        self.drawImGui()

    def drawImGui(self):
        if imgui.begin("Instrument Controls"):
            imgui.text("Position")
            any_changed = False
            changed, value = imgui.input_float(
                "X", self.instrument_pos[0], step=0.1
            )
            if changed:
                self.instrument_pos[0] = value
                any_changed = True
            changed, value = imgui.input_float(
                "Y", self.instrument_pos[1], step=0.1
            )
            if changed:
                self.instrument_pos[1] = value
                any_changed = True
            changed, value = imgui.input_float(
                "Z", self.instrument_pos[2], step=0.1
            )
            if changed:
                self.instrument_pos[2] = value
                any_changed = True
            if any_changed:
                self.instrument_obj.moveTo(*self.instrument_pos)

            imgui.end()

    def drawGleonsStereo(self):
        if self.connection is None:
            return

        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.fb)

        gl.glClearColor(0.0, 0.0, 0.0, 1.0)
        self.obj_shader.renderMaterialOnly(1)
        objectsToDraw = [self.instrument_obj]

        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        gl.glClear(gl.GL_DEPTH_BUFFER_BIT)

        gl.glViewport(0, 0, self.fb_width // 2, self.fb_height)
        self.stereoCamL.setAllUniforms()
        for obj in objectsToDraw:
            obj.draw()

        gl.glViewport(
            self.fb_width // 2,
            0,
            self.fb_width // 2,
            self.fb_height,
        )
        self.stereoCamR.setAllUniforms()
        for obj in objectsToDraw:
            obj.draw()

        arr = gl.glReadPixelsf(
            0,
            0,
            self.fb_width,
            self.fb_height,
            gl.GL_BGR,
        )

        # without this, a line seem to be wrapped into two lines and cause weird
        # interlacing like effects
        arr = arr.reshape((self.fb_height, self.fb_width, 3))

        # Because glReadPixels considers (0,0) as bottom-left corner
        arr = np.flip(arr, 0)

        try:
            self.connection.send_bytes(arr.tobytes())
        except (ConnectionResetError, BrokenPipeError):
            self.connection = None
            self.acceptStreamConnectionInBackground()

        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

    def acceptStreamConnectionInBackground(self):
        if self.connection is not None:
            return

        def start():
            self.connection = self.listener.accept()

        self.connectionThread = threading.Thread(target=start, daemon=True)
        self.connectionThread.start()

    def keyboard(self, key, action, mods):
        if key == glfw.KEY_TAB and action == glfw.PRESS:
            self.renderGleonsOnly = not self.renderGleonsOnly

        if key == glfw.KEY_BACKSPACE and action == glfw.PRESS:
            self.stereoCamActive = not self.stereoCamActive

    def run(self):
        self.window.run()
        self.listener.close()


if __name__ == "__main__":
    app = App()
    app.run()
