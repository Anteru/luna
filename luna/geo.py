from numbers import Number
import copy

class Vector2:
    def __init__ (self, *args):
        if len (args) == 1:
            assert (hasattr (args [0], '__len__') and len (args[0]) == 2)
            self.x = args [0][0]
            self.y = args [0][1]
        else:
            assert (len (args) == 2)
            assert (isinstance (args [0], Number))
            assert (isinstance (args [1], Number))
            self.x = args [0]
            self.y = args [1]

    def __repr__ (self):
        return 'Vector2 ({}, {})'.format (self.x, self.y)

    def __eq__ (self, other):
        if isinstance (other, Vector2):
            return self.x == other.x and self.y == other.y
        else:
            return self.x == other [0] and self.y == other [1]

    def __ne__ (self, other):
        return not self.__eq__ (other)

    def __len__(self):
        return 2

    def __getitem__ (self, key):
        if key == 0:
            return self.x
        elif key == 1:
            return self.y

    def __setitem__ (self, key, value):
        if key == 0:
            self.x = value
        elif key == 1:
            self.y = value

    def __iter__ (self):
        return iter([self.x, self.y])

    def __add__ (self, other):
        if isinstance (other, Vector2):
            return Vector2 (self.x + other.x, self.y + other.y)
        else:
            assert (hasattr (other, '__len__') and len (other) == 2)
            return (self.x + other [0], self.y + other [1])

    def __sub__ (self, other):
        if isinstance (other, Vector2):
            return Vector2 (self.x - other.x, self.y - other.y)
        else:
            assert (hasattr (other, '__len__') and len (other) == 2)
            return (self.x - other [0], self.y - other [1])

    def __imul__ (self, other):
        assert (isinstance (other, Number))
        self.x *= other
        self.y *= other

    def __mul__ (self, other):
        c = Vector2 (self.x, self.y)
        c *= other
        return c

class BoundingBox:
    def __init__ (self, minCorner = None, maxCorner = None):
        if minCorner is not None:
            self._min = Vector2 (minCorner)
        else:
            self._min = Vector2 (float ('inf'), float ('inf'))

        if maxCorner is not None:
            self._max = Vector2 (maxCorner)
        else:
            self._max = Vector2 (-float ('inf'), -float ('inf'))

    @staticmethod
    def FromPoints (points):
        result = BoundingBox ()
        result.MergePoints (points)
        return result

    def Merge (self, other):
        if isinstance (other, BoundingBox):
            self.MergePoints (other)
        elif isinstance (other, Vector2) or isinstance (other, tuple):
            self.MergePoint (other)

    def MergePoint (self, point):
        self._min.x = min (point [0], self._min.x)
        self._min.y = min (point [1], self._min.y)
        self._max.x = max (point [0], self._max.x)
        self._max.y = max (point [1], self._max.y)

    def MergePoints (self, points):
        for p in points:
            self.MergePoint (p)

    def Expand (self, amount):
        v = Vector2 (amount, amount)
        self._min -= v
        self._max += v

    def __len__ (self):
        return 2

    def __getitem__ (self, key):
        if key == 0:
            return self._min
        elif key == 1:
            return self._max

    def __iter__ (self):
        return iter([self._min, self._max])

    def GetMinimum (self):
        return self._min

    def GetMaximum (self):
        return self._max

    def GetWidth (self):
        return self._max.x - self._min.y

    def GetHeight (self):
        return self._max.y - self._min.y

    def GetSize (self):
        return Vector2 (self.GetWidth (), self.GetHeight ())
