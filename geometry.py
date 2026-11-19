from OpenGL.GL import *
import math
from matrix import *

class Point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def selfSubtract(self, point):
        self.x -= point.x
        self.y -= point.y
        self.z -= point.z

    def selfAdd(self, point):
        self.x += point.x
        self.y += point.y
        self.z += point.z
    
    def subtraction(self, point):
        return Point(self.x - point.x, self.y - point.y, self.z - point.z)

    def addition(self, point):
        return Point(self.x + point.x, self.y + point.y, self.z + point.z)

    def scalarMultiply(self, value):
        return Point(self.x * value, self.y * value, self.z * value)

    def dotProduct(self, point):
        return self.x * point.x + self.y * point.y + self.z * point.z

    def crossProduct(self, point):
        return Point(
            self.y * point.z - self.z * point.y,
            self.z * point.x - self.x * point.z,
            self.x * point.y - self.y * point.x
        )

    @staticmethod
    def normalize(point):
        mag = (point.x**2 + point.y**2 + point.z**2)**.5
        mag = mag if mag else 1
        return Point(point.x/mag, point.y/mag, point.z/mag)

# cuts a polygon (in camera space) at the plane z = near, keeping only what is in front of it
def clip_near(points, near):
    result = []
    for i in range(len(points)):
        a = points[i]
        b = points[(i + 1) % len(points)]

        a_inside = a.z >= near
        b_inside = b.z >= near

        # the edge crosses the plane: add the crossing point
        if a_inside != b_inside:
            t = (near - a.z) / (b.z - a.z)
            result.append(a.addition(b.subtraction(a).scalarMultiply(t)))

        if b_inside:
            result.append(b)

    return result

class Figure():
    def __init__(self, x, y, z):
        self.coord = Point(x, y, z)
        self.matrix = Matrix()
        
class Cube(Figure):
    # color = None keeps the colorful gradient; an (r, g, b) tuple paints the cube with a single color
    def __init__(self, x, y, z, apothem, color=None):
        super().__init__(x, y, z);

        self.points = [   
            Point(x - apothem, y + apothem, z - apothem),
            Point(x - apothem, y - apothem, z - apothem),
            Point(x + apothem, y - apothem, z - apothem),
            Point(x + apothem, y + apothem, z - apothem),
            
            Point(x + apothem, y + apothem, z + apothem),
            Point(x + apothem, y - apothem, z + apothem),
            Point(x - apothem, y - apothem, z + apothem),
            Point(x - apothem, y + apothem, z + apothem)
        ]

        self.planes = [   
            Plane(x, y, z - apothem, [self.points[0], self.points[1], self.points[2], self.points[3]], color),
            Plane(x + apothem, y, z, [self.points[3], self.points[2], self.points[5], self.points[4]], color),
            Plane(x, y, z + apothem, [self.points[4], self.points[5], self.points[6], self.points[7]], color),
            Plane(x - apothem, y, z, [self.points[7], self.points[6], self.points[1], self.points[0]], color),
            Plane(x, y - apothem, z, [self.points[7], self.points[0], self.points[3], self.points[4]], color),
            Plane(x, y + apothem, z, [self.points[1], self.points[6], self.points[5], self.points[2]], color)
        ]
    
    def translate(self, dx, dy, dz):
        self.matrix.translate(dx, dy, dz)

    def scale(self, sx, sy, sz):
        self.matrix.scale(sx, sy, sz)
    
    def rotateX(self, ang):
        self.matrix.translate(-self.coord.x, -self.coord.y, -self.coord.z)
        self.matrix.rotateX(ang*math.pi/180)
        self.matrix.translate(self.coord.x, self.coord.y, self.coord.z)

    def rotateY(self, ang):
        self.matrix.translate(-self.coord.x, -self.coord.y, -self.coord.z)
        self.matrix.rotateY(ang*math.pi/180)
        self.matrix.translate(self.coord.x, self.coord.y, self.coord.z)

    def rotateZ(self, ang):
        self.matrix.translate(-self.coord.x, -self.coord.y, -self.coord.z)
        self.matrix.rotateZ(ang*math.pi/180)
        self.matrix.translate(self.coord.x, self.coord.y, self.coord.z)

    def draw(self, canvas):
        for plane in self.planes:
            plane.draw(canvas)
    
    def update(self):
        # nothing to apply: skip the 9 matrix multiplications (matters with hundreds of cubes)
        if self.matrix.current == self.matrix.identity:
            return

        for point in self.points + [self.coord]:
            self.matrix.applyPoint(point)
        self.matrix.reset()

        # the points moved, so the normals and centers of the faces changed
        for plane in self.planes:
            plane.refresh()

class Plane(Figure):
    def __init__(self, x, y, z, points, color=None):
        super().__init__(x, y, z);

        self.points = points
        self.color = color

        # faces glued to another block (inside a floor or a tree) are never visible
        self.hidden = False

        self.triangles = [
            Triangle([points[0], points[1], points[2]]),
            Triangle([points[2], points[3], points[0]])
        ]

        self.refresh()

    # normal and center only change when the points move, so they are calculated once and stored
    def refresh(self):
        self.normal = self.getNormal()
        self.center = self.getCenter()

    def getNormal(self):
        # v2 x v1 points out of the cube (v1 x v2 points inwards with this point order)
        v1 = self.points[1].subtraction(self.points[0])
        v2 = self.points[3].subtraction(self.points[0])
        return Point.normalize(v2.crossProduct(v1))

    def getCenter(self):
        # average of the face's points
        center = Point(0, 0, 0)
        for p in self.points:
            center.selfAdd(p)
        return center.scalarMultiply(1 / len(self.points))

    # back-face culling: the face is visible only if its normal points towards the camera
    def isFacing(self, camera):
        toCamera = camera.coord.subtraction(self.center)
        return self.normal.dotProduct(toCamera) > 0

    def draw(self, canvas):
        if self.hidden:
            return
        if canvas.backfaceCulling and not self.isFacing(canvas.camera):
            return

        if self.color is None:
            for triangle in self.triangles:
                triangle.draw(canvas)
        else:
            self.drawColored(canvas)

        if canvas.showNormals:
            self.drawNormal(canvas, 20)

    # Minecraft-like shading: the top is the brightest, the bottom the darkest
    def shade(self):
        if self.normal.y > 0.5:
            return 1.0
        if self.normal.y < -0.5:
            return 0.5
        if abs(self.normal.z) > 0.5:
            return 0.8
        return 0.65

    # the whole face as one polygon (TRIANGLE_FAN splits it into the same 2 triangles)
    def drawColored(self, canvas):
        projected = canvas.projectPolygon(self.points)
        if not projected:
            return

        light = self.shade()
        r, g, b = self.color

        glColor3f(r * light, g * light, b * light)
        glBegin(GL_TRIANGLE_FAN)
        for vertex in projected:
            glVertex3f(*vertex)
        glEnd()

        # darker edges, so each block can be told apart
        glColor3f(r * light * 0.6, g * light * 0.6, b * light * 0.6)
        glBegin(GL_LINE_LOOP)
        for vertex in projected:
            glVertex3f(*vertex)
        glEnd()

    def drawNormal(self, canvas, length):
        center = self.center
        tip = center.addition(self.normal.scalarMultiply(length))

        start = canvas.projectPoint(center)
        end = canvas.projectPoint(tip)
        if start is None or end is None:
            return

        glColor3f(1, 1, 0)
        glBegin(GL_LINES)
        glVertex3f(*start)
        glVertex3f(*end)
        glEnd()


        

class Triangle():
    def __init__(self, points):
        self.p0, self.p1, self.p2 = points

    def draw(self, canvas):
        projected = canvas.projectPolygon([self.p0, self.p1, self.p2])
        if not projected:
            return

        # fill: TRIANGLE_FAN turns the polygon into triangles that share the first vertex
        # (3 vertices -> 1 triangle, 4 vertices -> 2 triangles: 0-1-2 and 0-2-3)
        colors = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0)]
        glBegin(GL_TRIANGLE_FAN)
        for vertex, color in zip(projected, colors):
            glColor3f(*color)
            glVertex3f(*vertex)
        glEnd()

        # stroke on top of the fill, so the edges stay visible
        glColor3f(1, 1, 1)
        glBegin(GL_LINE_LOOP)
        for vertex in projected:
            glVertex3f(*vertex)
        glEnd()