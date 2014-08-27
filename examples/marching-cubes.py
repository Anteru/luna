#!/usr/bin/env python3

from luna import *
import numpy as np
import random

def GetPointOnLine (p0, p1):
    p0 = np.array (p0)
    p1 = np.array (p1)

    bias = 0.3
    return (p0 + ((p1 - p0) / 2) * random.uniform (1 - bias, 1 + bias))

if __name__=='__main__':
    cubeSize = 64
    spacing = 32
    perspectiveShift = 24

    random.seed (5)

    d = Drawing (5 * (cubeSize + perspectiveShift) + 4 * spacing,
                 3 * (cubeSize + perspectiveShift) + 2 * spacing)

    cube = Group ()

    sx = 24
    sy = -16

    vtx = [
        # Near
        (0, 0),
        (cubeSize, 0),
        (0, cubeSize),
        (cubeSize, cubeSize),

        # Far
        (sx + 0, sy + 0),
        (sx + cubeSize, sy + 0),
        (sx + 0, sy + cubeSize),
        (sx + cubeSize, sy + cubeSize)
    ]

    # Near
    cube.Add (Line (vtx [0], vtx [1]))
    cube.Add (Line (vtx [2], vtx [3]))
    cube.Add (Line (vtx [0], vtx [2]))
    cube.Add (Line (vtx [1], vtx [3]))

    # Bridge
    cube.Add (Line (vtx [0 + 4], vtx [1 + 4]))
    cube.Add (Line (vtx [2 + 4], vtx [3 + 4]))
    cube.Add (Line (vtx [0 + 4], vtx [2 + 4]))
    cube.Add (Line (vtx [1 + 4], vtx [3 + 4]))

    # Far
    cube.Add (Line (vtx [0], vtx [0 + 4]))
    cube.Add (Line (vtx [1], vtx [1 + 4]))
    cube.Add (Line (vtx [2], vtx [2 + 4]))
    cube.Add (Line (vtx [3], vtx [3 + 4]))

    d.AddShared (cube)

    # points on edges
    # Edges are enumerated as follows
    # Top: Clockwise from (0, 0) : 0, 1, 2, 3
    # Middle: Clockwise: 4, 5, 6, 7
    # Bottom: Clockwise, 8, 9, 10, 11
    etx = [
        GetPointOnLine (vtx [2], vtx [3]),
        GetPointOnLine (vtx [3], vtx [7]),
        GetPointOnLine (vtx [7], vtx [6]),
        GetPointOnLine (vtx [6], vtx [2]),

        GetPointOnLine (vtx [0], vtx [2]),
        GetPointOnLine (vtx [1], vtx [3]),
        GetPointOnLine (vtx [5], vtx [7]),
        GetPointOnLine (vtx [4], vtx [6]),

        GetPointOnLine (vtx [0], vtx [1]),
        GetPointOnLine (vtx [1], vtx [5]),
        GetPointOnLine (vtx [5], vtx [4]),
        GetPointOnLine (vtx [4], vtx [0]),
    ]

    def CreateTriangle (edges):
        return Polygon ([etx [e] for e in edges],
            fill=Fill (Color (0xCC, 0xDD, 0xEE), opacity=0.33),
            stroke=Stroke (width=0.5))

    configurations = [
        [],
        [[0, 3, 4]],
        [[1, 3, 4], [1, 4, 5]],
        [[0, 3, 4], [5, 9, 8]],
        [[0, 5, 3], [5, 7, 3], [5, 6, 7]],
        [[4, 5, 6], [4, 6, 7]],
        [[4, 8, 11], [0, 5, 3], [5, 7, 3], [5, 6, 7]],
        [[0, 3, 4], [5, 9, 8], [1, 6, 2], [10, 11, 7]],
        [[4, 10, 11], [4, 10, 0], [10, 0, 6], [6, 0, 1]],
        [[3, 0, 11], [0, 11, 6], [0, 5, 6], [10, 11, 6]],
        [[0, 3, 4], [6, 10, 9]],
        [[1,5,4], [1, 3, 4], [6, 10, 9]],
        [[0, 1, 5], [4, 8, 11], [6, 10, 9]],
        [[0,3,11], [11, 8, 0], [1, 9, 10], [10, 2, 1]],
        [[4, 0, 7], [0, 7, 9], [0, 1, 9], [10, 7, 9]]
    ]

    interiorPoints = [
        [],
        [2],
        [2, 3],
        [2, 1],
        [3, 7],

        [2, 3, 6, 7],
        [3, 7, 0, 6],
        [2, 7, 1, 4],
        [2, 7, 6, 4],
        [3, 7, 6, 4],

        [2, 5],
        [2,3,5],
        [3, 0, 5],
        [0, 2, 5, 7],
        [2, 6, 7, 5]
    ]

    for y in range(3):
        for x in range (5):
            c = Group (translation=(x * (cubeSize + perspectiveShift + spacing),
                                    y * (cubeSize + perspectiveShift + spacing) - sy))

            idx = y * 5 + x
            c.Add (Instance (cube, (0, 0)))

            for p in interiorPoints [idx]:
                c.Add (Circle (vtx [p], radius=3, fill=Fill (Color (0xFF, 0x8, 0x8))))

            for t in configurations [idx]:
                c.Add (CreateTriangle (t))

            d.Add (c)

    d.SaveSvg ('marching-cubes.svg')
