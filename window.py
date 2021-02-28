import glfw


class Window:
    EVENT_CONSUMED = "CONSUMED"

    WIN_WIDTH = 480
    WIN_HEIGHT = 480
    WIN_ASPECT = WIN_WIDTH / WIN_HEIGHT

    def __init__(self, displayfn):
        self.window = None
        self.displayfn = displayfn
        self.keyboardfns = []
        self.mousefns = []
        self.scrollfns = []

    def setupContext(self):
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
        glfw.set_scroll_callback(window, self.scroll)
        glfw.make_context_current(window)

        self.window = window

    def reshape(self, window, width, height):
        glfw.set_window_size(self.window, self.WIN_WIDTH, self.WIN_HEIGHT)

    def keyboard(self, window, key, scancode, action, mods):
        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, glfw.TRUE)
            return

        for keyboardfn in self.keyboardfns:
            if keyboardfn(key, action, mods) == Window.EVENT_CONSUMED:
                break

    def screenToNDC(self, x, y):
        x -= self.width() / 2
        x /= self.width() / 2

        y -= self.height() / 2
        y /= self.height() / 2
        y = -y

        return (x, y)

    def mouse(self, window, btn, action, mods):
        for mousefn in self.mousefns:
            if (
                mousefn(btn, action, mods, False, None, None)
                == Window.EVENT_CONSUMED
            ):
                break

    def scroll(self, window, x, y):
        for scrollfn in self.scrollfns:
            if scrollfn(x, y) == Window.EVENT_CONSUMED:
                break

    def motion(self, window, x, y):
        warp = False
        if x > self.width():
            x = 0
            warp = True
        elif x < 0:
            x = self.width()
            warp = True
        if y > self.height():
            y = 0
            warp = True
        elif y < 0:
            y = self.height()
            warp = True

        if warp:
            glfw.set_cursor_pos(self.window, x, y)

        (x, y) = self.screenToNDC(x, y)

        for mousefn in self.mousefns:
            if mousefn(None, None, None, warp, x, y) == Window.EVENT_CONSUMED:
                break

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

    def addScrollHandler(self, fn):
        self.scrollfns.append(fn)

    def addMouseHandler(self, fn):
        self.mousefns.append(fn)

    def addKeyboardHandler(self, fn):
        self.keyboardfns.append(fn)
