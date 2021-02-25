import OpenGL.GL as gl


class Shader:
    vertexCode = """#version 330 core
    in vec3 position;

    void main() {
        gl_Position = vec4(position, 1.0);
    }
    """

    fragmentCode = """#version 330 core
    void main() {
        gl_FragColor = vec4(1.0, 1.0, 1.0, 1.0);
    }
    """

    def __init__(self):
        self.compiled = False
        self.program = None

    def setup(self):
        program = gl.glCreateProgram()
        vertex = gl.glCreateShader(gl.GL_VERTEX_SHADER)
        fragment = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)

        gl.glShaderSource(vertex, self.vertexCode)  # type: ignore
        gl.glShaderSource(fragment, self.fragmentCode)  # type: ignore

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

        self.program = program
        self.compiled = True

    def getAttribLocation(self, attrib):
        return gl.glGetAttribLocation(self.program, attrib)

    def use(self):
        assert (
            self.compiled
        ), "Please call setup() to compile the shader before use."
        gl.glUseProgram(self.program)
