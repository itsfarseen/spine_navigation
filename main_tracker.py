from frame import FrameMesh
from frame_shader import FrameShader
from volume_nii import VolumeNiiMesh
from volume_shader import VolumeShader
from utils import findRotMat
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
import select
import queue
import params
import cv2
import numpy as np
import time
from math import sqrt, tan, radians, asin, atan2
from pprint import pprint
import glm
import time
import params
from tracker import Tracker, full_img_width, full_img_height, fb_zoom
from time import sleep
import glfw
from window import Window


class App:
    def __init__(self):
        self.tracker = Tracker()

        self.window = Window("Instrument Tracker", self.display)
        # context has to be initialized before any function touches opengl
        self.window.setupContext()
        self.window.addKeyboardHandler(self.keyboard)
        self.window.setQuad(True)

        self.grid_shader = GridShader()
        self.grid_shader.compile()
        self.grid = GridMesh(self.grid_shader)
        self.grid.uploadMeshData()

        self.frame_shader = FrameShader()
        self.frame_shader.compile()
        self.frame = FrameMesh(self.frame_shader)
        self.frame.uploadMeshData()

        self.obj_shader = ObjShader()
        self.obj_shader.compile()
        self.operating_table_obj = ObjMesh(
            "./assets/OperatingTable.obj", self.obj_shader
        )
        self.operating_table_obj.uploadMeshData()
        self.instrument_obj = ObjMesh("./assets/instrument1.obj", self.obj_shader)
        self.instrument_obj.uploadMeshData()
        self.instrument_pos = [0, 1.0, 0.0]
        self.instrument_obj.moveTo(*self.instrument_pos)
        self.instrument_rot = [0, 0, 0]
        self.instrument_live = False

        self.volume_shader = VolumeShader()
        self.volume_shader.compile()
        # self.volume_obj = VolumeTestMesh(self.volume_shader)
        self.volume_obj = VolumeNiiMesh("ct/ct.nii.gz", self.volume_shader)
        self.volume_obj.uploadMeshData()
        self.volume_obj.moveTo(0, 1.1, 0)

        self.cameraX = Camera(
            1.0, [self.obj_shader, self.grid_shader, self.volume_shader], "orthographic"
        )
        self.cameraX.lookDir(1, 0, 0)
        self.cameraX.moveTo(-1, 1.0, 0)
        self.cameraX.zoom(-1.5)

        self.cameraY = Camera(
            1.0, [self.obj_shader, self.grid_shader, self.volume_shader], "orthographic"
        )
        self.cameraY.lookDir(0, -0.99, 0.01)
        self.cameraY.moveTo(0, 1, 0)
        self.cameraY.zoom(-1)

        self.cameraZ = Camera(
            1.0, [self.obj_shader, self.grid_shader, self.volume_shader], "orthographic"
        )
        self.cameraZ.lookDir(0, 0, -1)
        self.cameraZ.moveTo(0, 1.0, 2)

        self.camera_controls = CameraControls(
            [
                (-1, 0, 1, 1, self.cameraX),
                (-1, -1, 0, 0, self.cameraY),
                (0, -1, 1, 0, self.cameraZ),
            ]
        )
        self.camera_controls.installHandlers(self.window)

        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_FRAMEBUFFER_SRGB)

    def updateInstrument(self):
        instrPos, instrDir = self.tracker.getInstrCoords()

        if instrPos is not None:
            self.instrument_pos = [instrPos.x, instrPos.y, instrPos.z]
            self.instrument_obj.moveTo(*self.instrument_pos)

            instrDirOrig = glm.vec3(0, 0, 1)
            rotMat = findRotMat(instrDirOrig, instrDir)
            self.instrument_obj.rotationMat = rotMat
            self.instrument_live = True
        else:
            self.instrument_live = False

    def display(self):
        # gl.glClearColor(0.1, 0.15, 0.18, 1.0)
        gl.glClearColor(0.3, 0.4, 0.38, 1.0)
        self.obj_shader.renderMaterialOnly(-1)
        self.updateInstrument()

        objectsToDraw = [
            self.instrument_obj,
            self.operating_table_obj,
            self.volume_obj,
            self.grid,
        ]

        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        gl.glViewport(
            0,
            params.CAM_SENSOR_HEIGHT,
            params.CAM_SENSOR_WIDTH,
            params.CAM_SENSOR_HEIGHT,
        )
        self.cameraX.setAllUniforms()
        for obj in objectsToDraw:
            obj.draw()

        gl.glViewport(0, 0, params.CAM_SENSOR_WIDTH, params.CAM_SENSOR_HEIGHT)
        self.cameraY.setAllUniforms()
        for obj in objectsToDraw:
            obj.draw()

        gl.glViewport(
            params.CAM_SENSOR_WIDTH,
            0,
            params.CAM_SENSOR_WIDTH,
            params.CAM_SENSOR_HEIGHT,
        )
        self.cameraZ.setAllUniforms()
        for obj in objectsToDraw:
            obj.draw()

        gl.glViewport(
            params.CAM_SENSOR_WIDTH,
            params.CAM_SENSOR_HEIGHT,
            params.CAM_SENSOR_WIDTH,
            params.CAM_SENSOR_HEIGHT,
        )
        if (img := self.tracker.last_img) is not None or True:
            pass
            # img = cv2.resize(
            #     img, (params.CAM_SENSOR_WIDTH, params.CAM_SENSOR_HEIGHT)
            # )
            # img = np.zeros((480, 480, 3), dtype=np.uint8)
            # gl.glDrawPixels(
            #     params.CAM_SENSOR_WIDTH,
            #     params.CAM_SENSOR_HEIGHT,
            #     gl.GL_BGR,
            #     gl.GL_UNSIGNED_BYTE,
            #     img,
            # )

        gl.glViewport(
            0,
            0,
            params.CAM_SENSOR_WIDTH * 2,
            params.CAM_SENSOR_HEIGHT * 2,
        )
        gl.glDepthFunc(gl.GL_ALWAYS)
        self.frame.draw()
        gl.glDepthFunc(gl.GL_LESS)

        self.drawImGui()

    def drawImGui(self):
        if imgui.begin("Debug Info"):

            imgui.text("Position")

            any_changed = False
            changed, self.instrument_pos[0] = imgui.input_float(
                "X", self.instrument_pos[0], step=0.1
            )

            changed, self.instrument_pos[1] = imgui.input_float(
                "Y", self.instrument_pos[1], step=0.1
            )

            changed, self.instrument_pos[2] = imgui.input_float(
                "Z", self.instrument_pos[2], step=0.1
            )

            m = self.instrument_obj.getRotationMat()
            v = glm.vec4(0, 0, 1, 0)
            v = m * v
            imgui.text("X {:.3f} Y {:.3f} Z {:.3f}".format(v.x, v.y, v.z))

            imgui.end()

    def keyboard(self, key, action, mods):
        pass

    def run(self):
        self.window.run()


if __name__ == "__main__":
    app = App()
    app.run()
