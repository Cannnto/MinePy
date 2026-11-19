import glfw
import random
from OpenGL.GL import *
from geometry import *
from camera import *
from input import *
from world import *

WORLD = True

# True: back-face culling + z-buffer (faces drawn in the right order)
# False: both off, so the faces show up in the order they are drawn
BACKFACE_CULLING = True

class Canvas():
    def __init__(self):
        self.w = 940;
        self.h = 680;

        self.viewport = ViewPort(self.w, self.h)

        if WORLD:
            # a bit above the floor, looking slightly down
            self.camera = Camera(0, 40, -300)
            self.camera.pitch = -15
        else:
            self.camera = Camera(0, 0, -100)

        # anything closer to the camera than this is cut off
        self.near = 0.1

        # yellow lines on each face (debug)
        self.showNormals = not WORLD

        self.backfaceCulling = BACKFACE_CULLING

        glfw.init()
        self.window = glfw.create_window(self.w, self.h, "MinePy", None, None)
        glfw.make_context_current(self.window)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        # z from 0 to -1: the depth we send per vertex (see project) lives in [0, 1]
        glOrtho(-self.w/2, self.w/2, -self.h/2, self.h/2, 0, 1)
        glMatrixMode(GL_MODELVIEW)
        if WORLD:
            # sky blue
            glClearColor(0.53, 0.78, 0.95, 1.0)
        else:
            glClearColor(0, 0, 0, 1.0)

        # z-buffer: each pixel keeps the depth of what was drawn there,
        # and a new pixel is only drawn if it is closer (or equal, so the edges can be drawn over the fill)
        # it is turned on and off together with the back-face culling
        if BACKFACE_CULLING:
            glEnable(GL_DEPTH_TEST)
        else:
            glDisable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)

        # pushes the filled triangles slightly back, so the edge lines win the depth test
        glEnable(GL_POLYGON_OFFSET_FILL)
        glPolygonOffset(1, 1)
        
        if WORLD:
            # world: a big grass floor with trees around
            self.blockSize = 20
            self.floorY = -60
            self.floor = Floor(0, self.floorY, 0, 40, 40, self.blockSize)
            self.trees = self.random_trees(12)
            self.world = [self.floor] + self.trees
        else:
            # Cube also has update() and draw(), so the loop treats it like the floor and the trees
            self.world = [self.random_cube(50)] + [self.random_cube() for _ in range(8)]

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

    # trees on random floor cells, away from the camera and from each other
    def random_trees(self, amount):
        trees = []
        cells = []
        spawn = (round(self.camera.coord.x / self.blockSize), round(self.camera.coord.z / self.blockSize))

        while len(cells) < amount:
            i = random.randint(-18, 17)
            k = random.randint(-18, 17)
            if abs(i - spawn[0]) < 4 and abs(k - spawn[1]) < 4:
                continue
            if any(abs(i - ci) < 4 and abs(k - ck) < 4 for ci, ck in cells):
                continue
            cells.append((i, k))
            # the trunk starts one block above the floor
            trees.append(Tree(i * self.blockSize, self.floorY + self.blockSize, k * self.blockSize, self.blockSize))

        return trees

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

        for figure in self.world:
            figure.update()

    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        for figure in self.world:
            figure.draw(self)

    # lookAt x [x, y, z, 1], written out: same result as Matrix.multiply,
    # but much faster, since it runs for every vertex of every visible face
    def toCamera(self, point):
        m = self.camera.lookAt
        x, y, z = point.x, point.y, point.z
        return Point(
            m[0][0] * x + m[0][1] * y + m[0][2] * z + m[0][3],
            m[1][0] * x + m[1][1] * y + m[1][2] * z + m[1][3],
            m[2][0] * x + m[2][1] * y + m[2][2] * z + m[2][3]
        )

    def project(self, pointInCamera):
        vx = pointInCamera.x / pointInCamera.z * self.viewport.d
        vy = pointInCamera.y / pointInCamera.z * self.viewport.d
        cx = vx / self.viewport.w * self.w
        cy = vy / self.viewport.h * self.h

        # depth for the z-buffer: 0 at the near plane, approaching 1 far away.
        # it's based on 1/z because 1/z changes linearly across the projected triangle,
        # so OpenGL can interpolate it correctly between the vertices
        depth = 1 - self.near / pointInCamera.z

        # glOrtho looks towards -z, so the depth goes in negative
        return cx, cy, -depth

    # world point -> screen (canvas) coordinates + depth, or None if the point is behind the camera
    def projectPoint(self, point):
        pointInCamera = self.toCamera(point)
        if pointInCamera.z < self.near:
            return None
        return self.project(pointInCamera)

    # world polygon -> list of screen (canvas) vertices + depth, already cut at the near plane
    # returns an empty list if the polygon is entirely behind the camera
    def projectPolygon(self, points):
        inCamera = [self.toCamera(p) for p in points]

        clipped = clip_near(inCamera, self.near)
        if len(clipped) < 3:
            return []

        return [self.project(p) for p in clipped]

Canvas().run()