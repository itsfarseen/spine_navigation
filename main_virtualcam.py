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
from volume_shader import VolumeShader
from volume_nii import VolumeNiiMesh
from volume_test import VolumeTestMesh
import logging
import glfw
from camera_controls import CameraControls
import multiprocessing.connection as mpc
import time
import threading
import imgui
import select
import queue
import params


class App:
    def __init__(self):
        self.listener = mpc.Listener(("127.0.0.1", 5001), "AF_INET")
        self.connection = None
        self.connectionThread = None
        self.connectionDataQueue = queue.Queue(maxsize=1)
        self.acceptStreamConnectionInBackground()

        self.window = Window("Virtual Stereo Camera", self.display)
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
        self.instrument_obj = ObjMesh("./assets/instrument1.obj", self.obj_shader)
        self.instrument_obj.uploadMeshData()
        self.instrument_pos = [0, 1.0, -0.2]
        self.instrument_rot = [0, 0, 0]
        self.instrument_obj.moveTo(*self.instrument_pos)
        self.instrument_obj.setRotationX(self.instrument_rot[0])
        self.instrument_obj.setRotationY(self.instrument_rot[1])
        self.instrument_obj.setRotationZ(self.instrument_rot[2])

        self.volume_shader = VolumeShader()
        self.volume_shader.compile()
        # self.volume_obj = VolumeTestMesh(self.volume_shader)
        self.volume_obj = VolumeNiiMesh("ct/ct.nii.gz", self.volume_shader)
        self.volume_obj.uploadMeshData()
        self.volume_obj.moveTo(0, 1.1, 0)

        all_shaders = [self.grid_shader, self.obj_shader, self.volume_shader]

        self.stereoCamActive = False

        self.camera = Camera(1.0, all_shaders, "orthographic")
        self.cameraControls = CameraControls([(-1, -1, 1, 1, self.camera)])
        self.cameraControls.installHandlers(self.window)

        self.stereoCamL = Camera(1.0, all_shaders)
        self.stereoCamR = Camera(1.0, all_shaders)

        self.stereoCamL.moveTo(params.CAM_X_DELTA / 2, params.CAM_Y, params.CAM_Z)
        self.stereoCamR.moveTo(-params.CAM_X_DELTA / 2, params.CAM_Y, params.CAM_Z)

        stereoCamPose = params.CAM_POSE
        self.stereoCamL.lookDir(*stereoCamPose)
        self.stereoCamR.lookDir(*stereoCamPose)

        self.renderGleonsOnly = False

        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_FRAMEBUFFER_SRGB)

        fb_zoom = params.FB_ZOOM
        self.fb_width = params.CAM_SENSOR_WIDTH * 2 * fb_zoom
        self.fb_height = params.CAM_SENSOR_HEIGHT * fb_zoom

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
                self.operating_table_obj,
                self.instrument_obj,
                self.grid,
                self.volume_obj,
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
            changed, self.instrument_pos[0] = imgui.input_float(
                "X", self.instrument_pos[0], step=0.1
            )
            any_changed = changed or any_changed

            changed, self.instrument_pos[1] = imgui.input_float(
                "Y", self.instrument_pos[1], step=0.1
            )
            any_changed = changed or any_changed

            changed, self.instrument_pos[2] = imgui.input_float(
                "Z", self.instrument_pos[2], step=0.1
            )
            any_changed = changed or any_changed

            if any_changed:
                self.instrument_obj.moveTo(*self.instrument_pos)

            imgui.text("Rotation")

            changed, self.instrument_rot[0] = imgui.input_float(
                "X Rot", self.instrument_rot[0], step=1
            )
            if changed:
                self.instrument_obj.setRotationX(self.instrument_rot[0])

            changed, self.instrument_rot[1] = imgui.input_float(
                "Y Rot", self.instrument_rot[1], step=1
            )
            if changed:
                self.instrument_obj.setRotationY(self.instrument_rot[1])

            changed, self.instrument_rot[2] = imgui.input_float(
                "Z Rot", self.instrument_rot[2], step=1
            )
            if changed:
                self.instrument_obj.setRotationZ(self.instrument_rot[2])

            m = self.instrument_obj.getRotationMat()
            v = glm.vec4(0, 0, 1, 0)
            v = m * v
            imgui.text("X {:.3f} Y {:.3f} Z {:.3f}".format(v.x, v.y, v.z))

            imgui.end()

    def drawGleonsStereo(self):
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

        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

        if self.connectionDataQueue.full():
            return

        self.connectionDataQueue.put_nowait(arr)

    def acceptStreamConnectionInBackground(self):
        if self.connection is not None:
            return

        def start():
            while True:
                self.connection = self.listener.accept()
                while True:
                    arr = self.connectionDataQueue.get()
                    try:
                        self.connection.send_bytes(arr.tobytes())
                    except (ConnectionResetError, BrokenPipeError):
                        self.connection = None
                        break

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
