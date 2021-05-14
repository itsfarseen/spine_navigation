import params
import glm
import OpenGL.GL as gl
from utils import findRotMat


class Camera:
    def __init__(self, aspect, shader, projection="perspective"):
        self.shader = shader
        self.aspect = float(aspect)

        self.position = glm.vec3(0.0, 5.0, 5.0)
        self.lookAtPos = glm.vec3(0.0, 0.0, 0.0)

        worldUp = glm.vec3(0.0, 1.0, 0.0)

        self.right = glm.cross(self._principal(), worldUp)
        self.up = glm.cross(self.right, self._principal())

        self.fov_degrees = params.CAM_FOV_DEGREES

        self.projection = projection

    def _principal(self):
        return glm.normalize(self.lookAtPos - self.position)

    def setup(self):
        self.setAllUniforms()

    def setProjectionUniform(self):
        if self.projection == "perspective":
            proj = glm.perspective(
                glm.radians(self.fov_degrees), self.aspect, 0.1, 1000.0
            )
        elif self.projection == "orthographic":
            zoom_scale = glm.length(self.lookAtPos - self.position) / 2
            proj = glm.ortho(
                -zoom_scale,
                zoom_scale,
                -zoom_scale,
                zoom_scale,
                -1000.0,
                1000.0,
            )

        else:
            raise ValueError("Invalid projection", self.projection)
        if isinstance(self.shader, list):
            for shader in self.shader:
                shader.setProjectionMatrix(proj)
        else:
            self.shader.setProjectionMatrix(proj)

    def setViewUniform(self):

        view = glm.lookAt(self.position, self.position + self._principal(), self.up)
        rot = glm.inverse(glm.lookAt(glm.vec3(0, 0, 0), self._principal(), self.up))

        if isinstance(self.shader, list):
            for shader in self.shader:
                try:
                    shader.setViewMatrix(view)
                except AttributeError:
                    shader.setViewMatrix2(view=view, rot=rot)
        else:
            self.shader.setViewMatrix(view)

    def setAllUniforms(self):
        self.setProjectionUniform()
        self.setViewUniform()

    def moveTo(self, x, y, z):
        moveTo = glm.vec3(x, y, z)
        delta = moveTo - self.position
        self.position += delta
        self.lookAtPos += delta
        self.setViewUniform()

    def lookAt(self, x, y, z):
        self.lookAtPos = glm.vec3(x, y, z)
        self.setViewUniform()

    def lookDir(self, x, y, z):
        lookDir = glm.vec3(x, y, z)
        self.lookAtPos = self.position + lookDir
        self.setViewUniform()

    def rotate(self, x, y):
        x_factor = 90.0
        y_factor = 90.0

        x_rot_axis = glm.vec3(0, 1, 0)
        x_angle = glm.radians(-x * x_factor)
        rot_x = glm.rotate(glm.identity(glm.mat4), x_angle, x_rot_axis)
        self.right = glm.vec3(rot_x * glm.vec4(self.right, 0))
        self.up = glm.cross(self.right, self._principal())

        y_rot_axis = self.right
        y_angle = glm.radians(y * y_factor)
        rot_y = glm.rotate(glm.identity(glm.mat4), y_angle, y_rot_axis)
        self.up = glm.vec3(rot_y * glm.vec4(self.up, 0))

        rot = rot_x * rot_y
        posDir = glm.vec4(self.position - self.lookAtPos, 0.0)
        posDirRotated = rot * posDir
        self.position = self.lookAtPos + glm.vec3(posDirRotated)

        self.setViewUniform()

    def move(self, x, y):
        amt = 4.0
        delta = -amt * (x * self.right + y * self.up)
        self.position += delta
        self.lookAtPos += delta
        self.setViewUniform()

    def zoom(self, z):
        amt = 1.0
        delta = amt * z * self._principal()
        self.position += delta
        self.setViewUniform()
