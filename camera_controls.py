import glfw
from window import Window


class CameraControls:
    def __init__(self, camera):
        self.camera = camera

        self.last_x = None
        self.last_y = None
        self.mode = None

    def installHandlers(self, window):
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
