# vi: foldmethod=indent:
import OpenGL.GL as gl
import OpenGL.GLUT as glut
import nibabel as nib
import glm
import numpy as np
import ctypes
import matplotlib.pyplot as plt
from voxels import sphere

window = None

WIN_WIDTH = 480
WIN_HEIGHT = 480
WIN_ASPECT = WIN_WIDTH / WIN_HEIGHT

slice_no = 0
MIN_SLICE = 0
MAX_SLICE = 103

img_data = None
uv_z = 0.0
uv_z_loc = None


def setup():
    gl.glViewport(0, 0, WIN_WIDTH, WIN_HEIGHT)
    gl.glEnable(gl.GL_BLEND)
    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
    global uv_z_loc
    uv_z_loc = gl.glGetUniformLocation(program, "uv_z")
    gl.glUniform1f(uv_z_loc, 0.1)


def display():
    gl.glClearColor(0.3, 0.4, 0.38, 1.0)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)

    gl.glBindTexture(gl.GL_TEXTURE_3D, tex)
    gl.glBindVertexArray(vao)
    offset = ctypes.c_void_p(0)
    gl.glDrawElements(gl.GL_TRIANGLES, 6, gl.GL_UNSIGNED_INT, offset)  # type: ignore

    # mat_proj = glm.perspective(45, WIN_ASPECT, 0.01, 1000.0)
    glut.glutSwapBuffers()


def reshape(width, height):
    glut.glutReshapeWindow(WIN_WIDTH, WIN_HEIGHT)


def keyboard(key, x, y):
    global uv_z
    if key == b"\x1b":
        glut.glutLeaveMainLoop()
    elif key == b"a":
        uv_z = min(uv_z + 0.01, 1.0)
    elif key == b"z":
        uv_z = max(uv_z - 0.01, 0.0)

    gl.glUniform1f(uv_z_loc, uv_z)
    glut.glutPostRedisplay()


def mouse(btn, state, x, y):
    # if state == glut.GLUT_UP:
    #     # process only button press and not release
    #     # (scroll wheel movements are interpreted as button presses)
    #     return

    global slice_no, uv_z
    if btn == 3:  # scroll up
        slice_no = min(slice_no + 1, MAX_SLICE)
        uv_z = min(uv_z + 0.1, 1.0)
    elif btn == 4:  # scroll down
        uv_z = max(uv_z - 0.1, 0.0)


def setupWindow():
    global window
    glut.glutInit()
    glut.glutInitContextVersion(3, 3)
    glut.glutInitContextProfile(glut.GLUT_CORE_PROFILE)
    glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGBA)  # type: ignore
    window = glut.glutCreateWindow("Hello World [Float]")
    glut.glutReshapeFunc(reshape)
    glut.glutDisplayFunc(display)
    glut.glutMouseFunc(mouse)
    glut.glutKeyboardFunc(keyboard)


program = None


def setupShaders():
    vertexCode = """
#version 330 core
    in vec2 position;
    in vec2 uv_coord;

    out vec2 f_uv_coord;

    void main() {
        f_uv_coord = uv_coord;
        gl_Position = vec4(position, 0.0, 1.0);
    }
    """

    fragmentCode = """
#version 330 core
    in vec2 f_uv_coord;
    uniform float uv_z;
    uniform sampler3D ourTexture;
    void main() {
        vec4 col = texture(ourTexture, vec3(f_uv_coord.x, uv_z, f_uv_coord.y));
        gl_FragColor = vec4(col.r, col.r, col.r, col.r);
    }
    """

    global program
    program = gl.glCreateProgram()
    vertex = gl.glCreateShader(gl.GL_VERTEX_SHADER)
    fragment = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)

    gl.glShaderSource(vertex, vertexCode)  # type: ignore
    gl.glShaderSource(fragment, fragmentCode)  # type: ignore

    gl.glCompileShader(vertex)
    if not gl.glGetShaderiv(vertex, gl.GL_COMPILE_STATUS):
        error = gl.glGetShaderInfoLog(vertex).decode()
        raise RuntimeError("vertex shader compilation error", error)

    gl.glCompileShader(fragment)
    if not gl.glGetShaderiv(fragment, gl.GL_COMPILE_STATUS):
        error = gl.glGetShaderInfoLog(fragment).decode()
        raise RuntimeError("fragment shader compilation error", error)

    gl.glAttachShader(program, vertex)
    gl.glAttachShader(program, fragment)
    gl.glLinkProgram(program)

    if not gl.glGetProgramiv(program, gl.GL_LINK_STATUS):  # type: ignore
        error = gl.glGetProgramInfoLog(program)
        raise RuntimeError("shader linking error", error)

    gl.glDetachShader(program, vertex)
    gl.glDetachShader(program, fragment)

    gl.glUseProgram(program)


vao = None
vbo = None
ebo = None

tex = None


def setupModels():
    # load vbo data
    global vbo
    vbo = gl.glGenBuffers(1)  # type: ignore
    vbo_data = np.zeros((4, 4), dtype=np.float32)
    vbo_data[...] = (
        (-0.5, 0.5, 0.0, 1.0),
        (0.5, 0.5, 1.0, 1.0),
        (0.5, -0.5, 1.0, 0.0),
        (-0.5, -0.5, 0.0, 0.0),
    )
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
    gl.glBufferData(
        gl.GL_ARRAY_BUFFER, vbo_data.nbytes, vbo_data, gl.GL_DYNAMIC_DRAW
    )
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

    # load ebo data
    global ebo
    ebo = gl.glGenBuffers(1)  # type: ignore
    ebo_data = np.zeros((2, 3), dtype=np.uint32)
    ebo_data[...] = (0, 1, 2), (0, 2, 3)
    gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, ebo)
    gl.glBufferData(
        gl.GL_ELEMENT_ARRAY_BUFFER,
        ebo_data.nbytes,
        ebo_data,
        gl.GL_DYNAMIC_DRAW,
    )
    gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, 0)

    global vao
    vao = gl.glGenVertexArrays(1)  # type: ignore
    gl.glBindVertexArray(vao)

    # attach ebo to vao
    gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, ebo)

    # configure attributes
    stride = vbo_data.strides[0]
    offset = ctypes.c_void_p(0)
    loc = gl.glGetAttribLocation(program, "position")
    gl.glEnableVertexAttribArray(loc)

    # attach vbo to attrib (thus attaching vbo to vao)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
    gl.glVertexAttribPointer(loc, 2, gl.GL_FLOAT, False, stride, offset)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

    loc = gl.glGetAttribLocation(program, "uv_coord")
    gl.glEnableVertexAttribArray(loc)

    offset = ctypes.c_void_p(2 * 4)
    # attach vbo to attrib (thus attaching vbo to vao)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
    gl.glVertexAttribPointer(loc, 2, gl.GL_FLOAT, False, stride, offset)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

    gl.glBindVertexArray(0)

    img = nib.load("./ct/ct.nii.gz")
    global img_data
    img_data = img.get_fdata()

    # frame = np.ones((512, 512), dtype="byte") * 255

    global tex
    tex = gl.glGenTextures(1)  # type: ignore
    gl.glBindTexture(gl.GL_TEXTURE_3D, tex)
    gl.glTexParameter(gl.GL_TEXTURE_3D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    gl.glTexParameter(gl.GL_TEXTURE_3D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
    gl.glTexParameter(
        gl.GL_TEXTURE_3D, gl.GL_TEXTURE_WRAP_R, gl.GL_CLAMP_TO_BORDER
    )
    gl.glTexParameter(
        gl.GL_TEXTURE_3D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_BORDER
    )
    gl.glTexParameter(
        gl.GL_TEXTURE_3D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_BORDER
    )
    # note: load texture data moved to display()
    gl.glBindTexture(gl.GL_TEXTURE_3D, 0)

    frame = img_data[100:164, 100:164, 0:64]
    min_val = np.min(frame)
    frame -= min_val
    max_val = np.max(frame)
    frame /= max_val
    frame *= 255
    frame -= 70
    frame *= 2.0
    frame = np.clip(frame, 0, 255)
    frame = frame.astype("uint8")

    # frame = sphere(64, 64, 64, 20)*255
    # frame = frame.astype("uint8")
    # frame = np.array(frame)

    # frame = np.arange(256, dtype="uint8")
    # frame = np.tile(frame, 2 * 512 * 64)
    # frame = frame.astype("uint8")
    # frame = frame.reshape((512, 512, 64))
    # assert frame.shape == (512, 512, 64)

    gl.glBindTexture(gl.GL_TEXTURE_3D, tex)
    gl.glTexImage3D(
        gl.GL_TEXTURE_3D,
        0,
        gl.GL_RED,
        frame.shape[0],
        frame.shape[1],
        frame.shape[2],
        0,
        gl.GL_RED,
        gl.GL_UNSIGNED_BYTE,
        frame,
    )  # type: ignore
    gl.glBindTexture(gl.GL_TEXTURE_3D, 0)


def loadCt():
    img = nib.load("./ct/ct.nii.gz")
    img[0]


def main():
    setupWindow()
    setupShaders()
    setupModels()
    setup()
    glut.glutMainLoop()


if __name__ == "__main__":
    main()
