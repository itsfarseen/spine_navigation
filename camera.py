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
        amt = 4.0

        (cameraPrincipal, cameraRight, cameraUp) = self._getCamVecs()

        delta = amt * (x * cameraRight + y * cameraUp)

        self.position += delta

    def move(self, x, y):
        amt = 2.0

        (cameraPrincipal, cameraRight, cameraUp) = self._getCamVecs()

        delta = -amt * (x * cameraRight + y * cameraUp)

        self.position += delta
        self.lookAt += delta
