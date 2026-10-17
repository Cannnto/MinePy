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
        
        self.Cube = Cube(50, 0, 300, 50)

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
        dx = dy = dz = 0

        if glfw.get_key(self.window, glfw.KEY_D) == glfw.PRESS: dx += step
        if glfw.get_key(self.window, glfw.KEY_A) == glfw.PRESS: dx -= step
        if glfw.get_key(self.window, glfw.KEY_W) == glfw.PRESS: dy += step
        if glfw.get_key(self.window, glfw.KEY_S) == glfw.PRESS: dy -= step
        if glfw.get_key(self.window, glfw.KEY_K) == glfw.PRESS: dz += step
        if glfw.get_key(self.window, glfw.KEY_J) == glfw.PRESS: dz -= step

        self.Cube.move(dx, dy, dz)

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