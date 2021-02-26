import glfw


class Window:
    WIN_WIDTH = 480
    WIN_HEIGHT = 480
    WIN_ASPECT = WIN_WIDTH / WIN_HEIGHT

    def __init__(self, displayfn, keyboardfn=None, mousefn=None):
        self.window = None
        self.displayfn = displayfn
        self.keyboardfn = keyboardfn
        self.mousefn = mousefn

    def setup(self):
        glfw.init()
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.RESIZABLE, glfw.FALSE)

        window = glfw.create_window(
            self.WIN_WIDTH, self.WIN_HEIGHT, "Hello World [Float]", None, None
        )
        glfw.set_window_size_callback(window, self.reshape)
        glfw.set_mouse_button_callback(window, self.mouse)
        glfw.set_cursor_pos_callback(window, self.motion)
        glfw.set_key_callback(window, self.keyboard)
        glfw.make_context_current(window)

        self.window = window

    def reshape(self, window, width, height):
        glfw.set_window_size(self.window, self.WIN_WIDTH, self.WIN_HEIGHT)

    def keyboard(self, window, key, scancode, action, mods):
        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, glfw.TRUE)
            return

        if self.keyboardfn is not None:
            (self.keyboardfn)(key, action, mods)

    def screenToNDC(self, x, y):
        x -= self.width() / 2
        x /= self.width() / 2

        y -= self.height() / 2
        y /= self.height() / 2
        y = -y

        return (x, y)

    def mouse(self, window, btn, action, mods):
        if self.mousefn is not None:
            (self.mousefn)(btn, action, mods, None, None)

    def motion(self, window, x, y):
        (x, y) = self.screenToNDC(x, y)

        if self.mousefn is not None:
            (self.mousefn)(None, None, None, x, y)

    def run(self):
        while not glfw.window_should_close(self.window):
            self.displayfn()
            glfw.swap_buffers(self.window)
            glfw.poll_events()
        glfw.terminate()

    def width(self):
        return self.WIN_WIDTH

    def height(self):
        return self.WIN_HEIGHT

    def aspect(self):
        return self.WIN_ASPECT
