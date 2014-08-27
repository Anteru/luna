from enum import Enum, unique

@unique
class LineCap(Enum):
    Round   = 0
    Butt    = 1
    Square  = 2

@unique
class LineJoin(Enum):
    Miter = 0
    Round = 1
    Bevel = 2

@unique
class DashPattern (Enum):
    Dash = 0
    Dot = 1
    SparseDash = 2
    DashDot = 3

def _DashPatternToArray (p):
    m = {
        DashPattern.Dash: [5, 5],
        DashPattern.Dot: [1, 5],
        DashPattern.SparseDash: [5, 10],
        DashPattern.DashDot: [15, 10, 5, 10]
    }

    return m [p]

class Color:
    def __init__ (self, r, g = None, b = None):
        if g is None and b is None:
            self._r = r
            self._g = r
            self._b = r
        else:
            self._r = r
            self._g = g
            self._b = b

    def R (self):
        return self._r

    def G (self):
        return self._g

    def B (self):
        return self._b

class Stroke:
    def __init__ (self, color=Color(0), width=1, linecap=LineCap.Round,
        linejoin=LineJoin.Round, dashPattern=None,opacity=1):
        '''Specify a stroke style.

        A stroke style is used for stroking lines.

        dashPattern must be an array of numbers or alternatively a known pattern.'''
        self._color = color
        self._width = width
        self._linecap = linecap
        self._linejoin = linejoin

        self._opacity = opacity

        if isinstance (dashPattern, DashPattern):
            self._dashPattern = _DashPatternToArray (dashPattern)
        else:
            self._dashPattern = dashPattern

    def GetWidth (self):
        return self._width

    def GetColor (self):
        return self._color

    def GetLineCap (self):
        return self._linecap

    def GetLineJoin (self):
        return self._linejoin

    def GetDashPattern (self):
        return self._dashPattern

    def GetDashOffset (self):
        return 0

    def GetOpacity (self):
        return self._opacity

class Fill:
    def __init__ (self, color=Color (0), opacity=1):
        self._color = color
        self._opacity = opacity

    def GetColor (self):
        return self._color

    def GetOpacity (self):
        return self._opacity

class Element:
    def __init__(self, identifier=None):
        self._scale = (1, 1)
        self._children = []
        self._shared = []
        if identifier is None:
            self._id = self.__class__.__name__ + '_' + str(id(self))
            self._references = 0
        else:
            self._id = identifier
            # We assume this element is referenced from the "outside", as the
            # user has specified a name for it
            self._references = 1

    def GetId (self):
        return self._id

    def _AddReference (self):
        self._references += 1

    def IsReferenced (self):
        return self._references > 0

    def GetChildren (self):
        return self._children

    def GetShared (self):
        '''Get the shared elements referenced by this element.

        An element may instantiate an object multiple times to reduce the amount
        of processing.'''
        return self._shared

    def GetScale (self):
        return self._scale

    def Scale (self, x, y = None):
        if y is None:
            self._scale = (x, x)
        else:
            self._scale = (x, y)

class Line (Element):
    def __init__ (self, p0, p1, stroke=Stroke ()):
        super (Line, self).__init__ ()
        self._p0 = p0
        self._p1 = p1
        self._stroke = stroke

    def GetStart (self):
        return self._p0

    def GetEnd (self):
        return self._p1

    def GetStroke (self):
        return self._stroke

class Polygon (Element):
    def __init__ (self, points, stroke=Stroke (), fill=Fill ()):
        super(Polygon, self).__init__ ()
        self._points = points
        self._stroke = stroke
        self._fill = fill

    def GetPoints (self):
        return self._points

    def GetStroke (self):
        return self._stroke

    def GetFill (self):
        return self._fill

class Circle (Element):
    def __init__ (self, center, radius=1, stroke=Stroke (), fill=Fill ()):
        super (Circle, self).__init__ ()
        self._center = center
        self._radius = radius
        self._stroke = stroke
        self._fill = fill

    def GetStroke (self):
        return self._stroke

    def GetRadius (self):
        return self._radius

    def GetCenter (self):
        return self._center

    def GetFill (self):
        return self._fill

class Rectangle (Element):
    def __init__ (self, position, size, stroke=Stroke (), fill=Fill ()):
        super (Rectangle, self).__init__ ()
        self._position = position
        self._size = size
        self._stroke = stroke
        self._fill = fill

    def GetStroke (self):
        return self._stroke

    def GetSize (self):
        return self._size

    def GetPosition (self):
        return self._position

    def GetFill (self):
        return self._fill

class Instance (Element):
    def __init__ (self, source, position):
        super (Instance, self).__init__ ()
        source._AddReference ()
        self._source = source
        self._position = position

    def GetSource (self):
        return self._source

    def GetPosition (self):
        return self._position

class Group (Element):
    def __init__(self, translation=(0, 0), name=None):
        super(Group, self).__init__ ()
        self._name = name
        self._translation = translation

    def Add (self, item):
        self._children.append (item)

    def GetTranslation (self):
        return self._translation

class Drawing (Element):
    def __init__(self, width, height, margin = 4):
        '''Create a new drawing.

        Margin sets a margin around the drawing and thus increases the actual
        size. This is useful if a rectangle is drawn around the whole image;
        without the margin, parts of the line might be cut off.'''
        super(Drawing, self).__init__ ()
        self._width = width
        self._height = height
        self._margin = margin

    def Add (self, item):
        self._children.append (item)

    def GetWidth (self):
        return self._width

    def GetHeight (self):
        return self._height

    def GetMargin (self):
        return self._margin

    def SaveSvg (self, filename):
        from .backends.svg import SvgVisitor
        v = SvgVisitor ()
        v.Save (filename, self)

    def SavePng (self, filename):
        from .backends.cairo import CairoVisitor
        v = CairoVisitor ()
        v.SavePng (filename, self)

    def SavePdf (self, filename):
        from .backends.cairo import CairoVisitor
        v = CairoVisitor ()
        v.SavePdf (filename, self)

    def AddShared (self, item):
        '''Add a new, shared element.

        This element will be invisible by default. To place it in the drawing,
        use an Instance which references this object.'''
        self._shared.append (item)
        return item

class Grid (Group):
    def __init__ (self, offset, size, spacing, stroke=Stroke ()):
        super(Grid, self).__init__ ()
        horizontalLine = Line ((offset [0], offset [1]),
                      (offset [0] + size [0] * spacing, offset [1]),
                      stroke=stroke)
        self._shared.append (horizontalLine)

        for y in range (0, size [1] + 1):
            self.Add (Instance (horizontalLine, (0, y * spacing)))

        verticalLine = Line ((offset [0], offset [1]),
                             (offset [0], offset [1] + size [1] * spacing),
                             stroke=stroke)
        self._shared.append (verticalLine)
        for x in range (0, size [0] + 1):
            self.Add (Instance (verticalLine, (x * spacing, 0)))

class Cross (Group):
    def __init__ (self, position, size=1, stroke=Stroke()):
        super(Cross, self).__init__ ()
        self.Add (Line ((position [0] - size, position [1] - size),
                        (position [0] + size, position [1] + size),
                        stroke = stroke))
        self.Add (Line ((position [0] + size, position [1] - size),
                        (position [0] - size, position [1] + size),
                        stroke = stroke))

class Visitor:
    def VisitGeneric (self, element, ctx=None):
        fname = 'Visit{0}'.format (element.__class__.__name__)

        if hasattr (self, fname):
            func = getattr (self, fname)
            return func (element, ctx)
        else:
            return self.VisitElement (element, ctx)

    def VisitElement (self, element, ctx=None):
        pass