import OpenGL.GLUT as glut

class Window:
    WIN_WIDTH = 480
    WIN_HEIGHT = 480
    WIN_ASPECT = WIN_WIDTH / WIN_HEIGHT

    def __init__(self, displayfn):
        self.window = None
        self.displayfn = displayfn

    def setup(self):
        global window
        glut.glutInit()
        glut.glutInitContextVersion(3, 3)
        glut.glutInitContextProfile(glut.GLUT_CORE_PROFILE)
        glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGBA)  # type: ignore
        window = glut.glutCreateWindow("Hello World [Float]")
        glut.glutReshapeFunc(self.reshape)
        glut.glutDisplayFunc(self.displayfn)
        glut.glutMouseFunc(self.mouse)
        glut.glutKeyboardFunc(self.keyboard)

    def reshape(self, width, height):
        glut.glutReshapeWindow(self.WIN_WIDTH, self.WIN_HEIGHT)

    def keyboard(self, key, x, y):
        if key in (b"q",):
            glut.glutLeaveMainLoop()
            return
        glut.glutPostRedisplay()

    def mouse(self, btn, state, x, y):
        if state == glut.GLUT_UP:
            # process only button press and not release
            # (scroll wheel movements are interpreted as button presses)
            return
        glut.glutPostRedisplay()

    def run(self):
        glut.glutMainLoop()

    def width(self):
        return self.WIN_WIDTH

    def height(self):
        return self.WIN_HEIGHT

    def aspect(self):
        return self.WIN_ASPECT
