from geometry import *

GRASS = (0.42, 0.75, 0.24)
WOOD = (0.45, 0.30, 0.16)
LEAVES = (0.18, 0.52, 0.14)

# index of each face inside Cube.planes -> direction of the neighbour that would cover it
FACE_DIRECTIONS = [
    (0, 0, -1),  # 0: front (z - apothem)
    (1, 0, 0),   # 1: right (x + apothem)
    (0, 0, 1),   # 2: back  (z + apothem)
    (-1, 0, 0),  # 3: left  (x - apothem)
    (0, 1, 0),   # 4: top   (y + apothem)
    (0, -1, 0),  # 5: bottom (y - apothem)
]


# blocks is a dict {(i, j, k): cube} on a grid.
# a face touching another block of the same structure can never be seen, so it is hidden
def hideSharedFaces(blocks):
    for (i, j, k), cube in blocks.items():
        for face, (di, dj, dk) in enumerate(FACE_DIRECTIONS):
            if (i + di, j + dj, k + dk) in blocks:
                cube.planes[face].hidden = True


class Structure():
    # (x, y, z) is the center of the block at grid position (0, 0, 0)
    def __init__(self, x, y, z, size):
        self.x, self.y, self.z = x, y, z
        self.size = size
        self.blocks = {}

    def addBlock(self, i, j, k, color):
        half = self.size / 2
        self.blocks[(i, j, k)] = Cube(self.x + i * self.size,
                                      self.y + j * self.size,
                                      self.z + k * self.size,
                                      half, color)

    def update(self):
        for cube in self.blocks.values():
            cube.update()

    def draw(self, canvas):
        for cube in self.blocks.values():
            cube.draw(canvas)


class Floor(Structure):
    # a flat layer of width x depth grass blocks, centered on (x, z)
    def __init__(self, x, y, z, width, depth, size, color=GRASS):
        super().__init__(x, y, z, size)

        for i in range(-(width // 2), width - width // 2):
            for k in range(-(depth // 2), depth - depth // 2):
                self.addBlock(i, 0, k, color)

        hideSharedFaces(self.blocks)

        # nobody looks at the floor from below
        for cube in self.blocks.values():
            cube.planes[5].hidden = True


class Tree(Structure):
    # (x, y, z) is the center of the lowest trunk block
    def __init__(self, x, y, z, size, trunkHeight=4):
        super().__init__(x, y, z, size)

        for j in range(trunkHeight):
            self.addBlock(0, j, 0, WOOD)

        # two 3x3 layers of leaves around the top of the trunk
        for j in (trunkHeight - 1, trunkHeight):
            for i in (-1, 0, 1):
                for k in (-1, 0, 1):
                    if (i, j, k) not in self.blocks:
                        self.addBlock(i, j, k, LEAVES)

        # a "+" on top
        for i, k in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
            self.addBlock(i, trunkHeight + 1, k, LEAVES)

        hideSharedFaces(self.blocks)
