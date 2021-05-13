import OpenGL.GL as gl
import glm


class Shader:
    def __init__(self, vertexCode, fragmentCode):
        self.compiled = False
        self.program = None
        self.vertexCode = vertexCode
        self.fragmentCode = fragmentCode
        self.loc_cache = {}

    def compile(self):
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

    def _getAttribLocation(self, attrib):
        if attrib in self.loc_cache:
            return self.loc_cache[attrib]
        loc = gl.glGetAttribLocation(self.program, attrib)
        self.loc_cache[attrib] = loc
        return loc

    def _getUniformLocation(self, uniform):
        if uniform in self.loc_cache:
            return self.loc_cache[uniform]
        loc = gl.glGetUniformLocation(self.program, uniform)
        self.loc_cache[uniform] = loc
        return loc

    def _setFloat(self, name, val):
        self.use()
        loc = self._getUniformLocation(name)
        assert loc != -1, name
        gl.glUniform1f(loc, val)

    def _setInt(self, name, val):
        self.use()
        loc = self._getUniformLocation(name)
        assert loc != -1, name
        gl.glUniform1i(loc, val)

    def _setVec3(self, name, val):
        self.use()
        loc = self._getUniformLocation(name)
        assert loc != -1, name
        if hasattr(val, "x"):
            gl.glUniform3f(loc, val.x, val.y, val.z)
        else:
            gl.glUniform3f(loc, val[0], val[1], val[2])

    def _setMat4(self, name, val):
        self.use()
        loc = self._getUniformLocation(name)
        assert loc != -1, name
        gl.glUniformMatrix4fv(loc, 1, False, glm.value_ptr(val))  # type: ignore

    def use(self):
        assert self.compiled, "Please call compile() to compile the shader before use."
        gl.glUseProgram(self.program)
