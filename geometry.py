from OpenGL.GL import *

class Point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class Figure():
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        
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
    
    def move(self, dx, dy, dz):
        self.x += dx
        self.y += dy
        self.z += dz
        for point in self.points:
            point.x += dx
            point.y += dy
            point.z += dz

    def draw(self, canvas):
        for plane in self.planes:
            plane.draw(canvas)

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