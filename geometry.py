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

class Figure():
    def __init__(self, x, y, z):
        self.coord = Point(x, y, z)
        self.matrix = Matrix()
        
class Cube(Figure):
    def __init__(self, x, y, z, apothem):
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
            Plane(x, y, z - apothem, [self.points[0], self.points[1], self.points[2], self.points[3]]),
            Plane(x + apothem, y, z, [self.points[3], self.points[2], self.points[5], self.points[4]]),
            Plane(x, y, z + apothem, [self.points[4], self.points[5], self.points[6], self.points[7]]),
            Plane(x - apothem, y, z, [self.points[7], self.points[6], self.points[1], self.points[0]]),
            Plane(x, y - apothem, z, [self.points[7], self.points[0], self.points[3], self.points[4]]),
            Plane(x, y + apothem, z, [self.points[1], self.points[6], self.points[5], self.points[2]])
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
        for point in self.points + [self.coord]:
            self.matrix.applyPoint(point)
        self.matrix.reset()

class Plane(Figure):
    def __init__(self, x, y, z, points):
        super().__init__(x, y, z);

        self.triangles = [   
            Triangle([points[0], points[1], points[2]]),
            Triangle([points[2], points[3], points[0]])
        ]        

    def draw(self, canvas):
        for triangle in self.triangles:
            triangle.draw(canvas)

class Triangle():
    def __init__(self, points):
        self.p0, self.p1, self.p2 = points

    def draw(self, canvas):
        p0x, p0y = canvas.project(self.p0)
        p1x, p1y = canvas.project(self.p1)
        p2x, p2y = canvas.project(self.p2)

        # glBegin(GL_TRIANGLES)
        glBegin(GL_LINE_LOOP)
        glColor3f(1, 0, 0); glVertex2f(p0x, p0y)
        glColor3f(0, 1, 0); glVertex2f(p1x, p1y)
        glColor3f(0, 0, 1); glVertex2f(p2x, p2y)
        glEnd()