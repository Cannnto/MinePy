import math

class Matrix:
    def __init__(self):
        self.identity = [
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ]
        
        self.current = [row[:] for row in self.identity]

    def multiply(self, matrix1, matrix2):
        result = []

        for lin, _ in enumerate(matrix1):
            result.append([]);  
            for col, _ in enumerate(matrix2[0]):
                cell = 0;
                for i, _ in enumerate(matrix2):
                    cell += matrix1[lin][i] * matrix2[i][col]
                result[lin].append(cell)

        return result

    def translate(self, dx, dy, dz):
        self.current = self.multiply([
            [1, 0, 0, dx],
            [0, 1, 0, dy],
            [0, 0, 1, dz],
            [0, 0, 0, 1]
        ], self.current) 

    def scale(self, sx, sy, sz):
        self.current = self.multiply([
            [sx, 0, 0, 0],
            [0, sy, 0, 0],
            [0, 0, sz, 0],
            [0, 0, 0, 1]
        ], self.current) 

    def rotateX(self, rad):
        self.current = self.multiply([
            [1, 0, 0, 0],
            [0, math.cos(rad), - math.sin(rad), 0],
            [0, math.sin(rad), math.cos(rad), 0],
            [0, 0, 0, 1]
        ], self.current) 

    def rotateY(self, rad):
        self.current = self.multiply([
            [math.cos(rad), 0, math.sin(rad), 0],
            [0, 1, 0, 0],
            [- math.sin(rad), 0, math.cos(rad), 0],
            [0, 0, 0, 1]
        ], self.current) 

    def rotateZ(self, rad):
        self.current = self.multiply([
            [math.cos(rad), - math.sin(rad), 0, 0],
            [math.sin(rad), math.cos(rad), 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ], self.current) 

    def reset(self):
        self.current = [row[:] for row in self.identity]

    def applyPoint(self, point):
        newPoint = self.multiply(self.current, [
            [point.x],
            [point.y],
            [point.z],
            [1]
        ])

        point.x, point.y, point.z = newPoint[0][0], newPoint[1][0], newPoint[2][0]  