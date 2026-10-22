import glfw
import random
from OpenGL.GL import *
from geometry import *
from camera import *
from input import *

class Canvas():
    def __init__(self):
        self.w = 940;
        self.h = 680;

        self.viewport = ViewPort(self.w, self.h)
        self.camera = Camera(0, 0, -100)

        # anything closer to the camera than this is cut off
        self.near = 0.1

        glfw.init()
        self.window = glfw.create_window(self.w, self.h, "MinePy", None, None)
        glfw.make_context_current(self.window)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-self.w/2, self.w/2, -self.h/2, self.h/2, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glClearColor(0, 0, 0, 1.0)
        
        self.Cubes = [
            self.random_cube(50),
            self.random_cube(),
            self.random_cube(),
            self.random_cube(),
            self.random_cube(),
            self.random_cube(),
            self.random_cube(),
            self.random_cube(),
            self.random_cube()
        ]

        # units per second
        self.speed = 200
        self.input = Input(self.window, self.camera, self.speed)
        self.last_time = glfw.get_time()

    def random_cube(self, size=None):
        if size is None:
            size = 10 + 50 * random.random()
        z = 200 + 200 * random.random()

        # visible area at the depth of the cube's front face, minus its size so it fits entirely
        half_w = (z - size) * (self.viewport.w / 2) / self.viewport.d - size
        half_h = (z - size) * (self.viewport.h / 2) / self.viewport.d - size

        x = (random.random() * 2 - 1) * half_w
        y = (random.random() * 2 - 1) * half_h
        return Cube(x, y, z, size)

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

        self.input.update(dt)

        self.camera.update()
        
        for cube in self.Cubes:
            cube.update()

    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT)
        for cube in self.Cubes:
            cube.draw(self)
    
    def toCamera(self, point):
        pCam = self.camera.matrix.multiply(self.camera.lookAt, [[point.x], [point.y], [point.z], [1]])
        return Point(pCam[0][0], pCam[1][0], pCam[2][0])

    def project(self, pointInCamera):
        vx = pointInCamera.x / pointInCamera.z * self.viewport.d
        vy = pointInCamera.y / pointInCamera.z * self.viewport.d
        cx = vx / self.viewport.w * self.w
        cy = vy / self.viewport.h * self.h
        return cx, cy

Canvas().run()