from geometry import * 

class ViewPort():
    def __init__(self, Cw, Ch):
        self.w = 2
        self.h = Ch/Cw * 2

        # distance between camera and viewport
        self.d = 1

class Camera():
    def __init__(self, x, y, z):
        self.coord = Point(x, y, z)

        self.matrix = Matrix()
        self.lookAt = [
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
        ]

        self.front = Point(0, 0, 3)
        self.upVector = Point(0, 1, 0)

        self.directionAxis = Point(0,0,0)
        self.rightAxis = Point(0,0,0)
        self.upAxis = Point(0,0,0)

        # in degrees; yaw = 90 makes the camera start looking towards +Z
        self.pitch = 0
        self.yaw = 90

        self.update()

    def update(self):
        yaw = math.radians(self.yaw)
        pitch = math.radians(self.pitch)
        self.directionAxis.x = math.cos(yaw) * math.cos(pitch)
        self.directionAxis.y = math.sin(pitch)
        self.directionAxis.z = math.sin(yaw) * math.cos(pitch)
        self.directionAxis = Point.normalize(self.directionAxis)

        self.rightAxis = Point.normalize(self.upVector.crossProduct(self.directionAxis))
        self.upAxis = self.directionAxis.crossProduct(self.rightAxis)

        self.lookAt = self.matrix.multiply([
            [self.rightAxis.x,      self.rightAxis.y,       self.rightAxis.z,       0],
            [self.upAxis.x,         self.upAxis.y,          self.upAxis.z,          0],
            [self.directionAxis.x,  self.directionAxis.y,   self.directionAxis.z,   0],
            [0,                     0,                      0,                      1]
        ],[
            [1, 0, 0, -self.coord.x],
            [0, 1, 0, -self.coord.y],
            [0, 0, 1, -self.coord.z],
            [0, 0, 0, 1],
        ]);
