import glm
import OpenGL.GL as gl


class Camera:
    def __init__(self):
        self.cameraUniform = None  # set by setup()

        self.position = glm.vec3(0.0, 5.0, 5.0)
        self.lookAt = glm.vec3(0.0, 0.0, 0.0)

    def setup(self, shader, window):
        self.window = window
        self.cameraUniform = shader.getUniformLocation("camera")

    def _getCamVecs(self):
        worldUp = glm.vec3(0.0, 1.0, 0.0)

        cameraPrincipal = glm.normalize(self.lookAt - self.position)
        cameraRight = glm.normalize(glm.cross(cameraPrincipal, worldUp))
        cameraUp = glm.normalize(glm.cross(cameraRight, cameraPrincipal))
        return (cameraPrincipal, cameraRight, cameraUp)

    def update(self):
        (cameraPrincipal, cameraRight, cameraUp) = self._getCamVecs()

        view = glm.lookAt(
            self.position, self.position + cameraPrincipal, glm.vec3(0, 1, 0)
        )
        proj = glm.perspective(
            glm.radians(45.0), self.window.aspect(), 0.1, 100.0
        )
        cameraMatrix = proj * view
        gl.glUniformMatrix4fv(
            self.cameraUniform, 1, False, glm.value_ptr(cameraMatrix)
        )  # type: ignore

    def rotate(self, x, y):
        x_factor = 90.0
        y_factor = 90.0
        (cameraPrincipal, cameraRight, cameraUp) = self._getCamVecs()

        # x_rot_axis = glm.vec3(0,1,0)
        x_rot_axis = cameraUp
        x_angle = glm.radians(-x * x_factor)
        rot_x = glm.rotate(glm.identity(glm.mat4), x_angle, x_rot_axis)

        y_rot_axis = cameraRight
        y_angle = glm.radians(y * y_factor)
        rot_y = glm.rotate(glm.identity(glm.mat4), y_angle, y_rot_axis)

        rot = rot_y * rot_x
        posDir = glm.vec4(self.position - self.lookAt, 0.0)
        posDirRotated = rot * posDir
        self.position = self.lookAt + glm.vec3(posDirRotated)

    def move(self, x, y):
        amt = 4.0

        (cameraPrincipal, cameraRight, cameraUp) = self._getCamVecs()

        delta = -amt * (x * cameraRight + y * cameraUp)

        self.position += delta
        self.lookAt += delta
