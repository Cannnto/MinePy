import glfw
from OpenGL.GL import *
from geometry import *

class ViewPort():
    def __init__(self):
        self.w = 1
        self.h = 0.75

        #distance between camera and viewport
        self.d = 1

class Canvas():
    def __init__(self):
        self.viewport = ViewPort()
        
        self.w = 640;
        self.h = 480;
        
        glfw.init()
        self.window = glfw.create_window(self.w, self.h, "MinePy", None, None)
        glfw.make_context_current(self.window)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-320, 320, -240, 240, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glClearColor(0, 0, 0, 1.0)
        
        self.Cube = Cube(0, 0, 300, 50)

        # units per second
        self.speed = 200
        self.last_time = glfw.get_time()

    def run(self):
        while not glfw.window_should_close(self.window):

            self.update()
            self.draw()

            glfw.swap_buffers(self.window)
            glfw.poll_events()

        glfw.terminate()
    
    def update(self):
        # time since the last frame, so the speed doesn't depend on FPS
        now = glfw.get_time()
        dt = now - self.last_time
        self.last_time = now

        step = self.speed * dt

        if glfw.get_key(self.window, glfw.KEY_D) == glfw.PRESS: self.Cube.translate(step, 0, 0)
        if glfw.get_key(self.window, glfw.KEY_A) == glfw.PRESS: self.Cube.translate(-step, 0, 0)
        if glfw.get_key(self.window, glfw.KEY_W) == glfw.PRESS: self.Cube.translate(0, step, 0)
        if glfw.get_key(self.window, glfw.KEY_S) == glfw.PRESS: self.Cube.translate(0, -step, 0)
        if glfw.get_key(self.window, glfw.KEY_K) == glfw.PRESS: self.Cube.translate(0, 0, step)
        if glfw.get_key(self.window, glfw.KEY_J) == glfw.PRESS: self.Cube.translate(0, 0, -step)

        if glfw.get_key(self.window, glfw.KEY_U) == glfw.PRESS: self.Cube.rotateX(step)
        if glfw.get_key(self.window, glfw.KEY_I) == glfw.PRESS: self.Cube.rotateY(step)
        if glfw.get_key(self.window, glfw.KEY_O) == glfw.PRESS: self.Cube.rotateZ(step)

        # if glfw.get_key(self.window, glfw.KEY_U) == glfw.PRESS: self.Cube.scale(step)
        # if glfw.get_key(self.window, glfw.KEY_I) == glfw.PRESS: self.Cube.rotateY(step)
        # if glfw.get_key(self.window, glfw.KEY_O) == glfw.PRESS: self.Cube.rotateZ(step)

        self.Cube.update()

    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT)
        self.Cube.draw(self)

    def project(self, point):
        vx = point.x / point.z * self.viewport.d
        vy = point.y / point.z * self.viewport.d
        cx = vx / self.viewport.w * self.w
        cy = vy / self.viewport.h * self.h
        return cx, cy

Canvas().run()