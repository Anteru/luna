import svgwrite
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
    def __init__ (self, color=Color(0), width=1, linecap=LineCap.Round, linejoin=LineJoin.Round):
        self._color = color
        self._width = width
        self._linecap = linecap
        self._linejoin = linejoin

    def GetWidth (self):
        return self._width

    def GetColor (self):
        return self._color

    def GetLineCap (self):
        return self._linecap

    def GetLineJoin (self):
        return self._linejoin

class Fill:
    def __init__ (self, color=Color (0)):
        self._color = color

    def GetColor (self):
        return self._color

class Element:
    def __init__(self):
        self._scale = (1, 1)
        self._children = []

    def GetChildren (self):
        return self._children

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

class Group (Element):
    def __init__(self, name=None):
        super(Group, self).__init__ ()
        self._name = name

    def Add (self, item):
        self._children.append (item)

class Drawing (Group):
    def __init__(self, width, height):
        super(Drawing, self).__init__ ()
        self._width = width
        self._height = height

    def GetWidth (self):
        return self._width

    def GetHeight (self):
        return self._height

    def SaveSvg (self, filename):
        v = SvgVisitor (filename)
        v.Save (self)

class Grid (Group):
    def __init__ (self, offset, size, spacing, stroke=Stroke ()):
        super(Grid, self).__init__ ()
        for y in range (size [1] + 1):
            ly = y * spacing + offset [1]
            self.Add (Line ((offset [0], ly),
                            (offset [0] + size [0] * spacing, ly),
                            stroke=stroke))
        for x in range (size [0] + 1):
            lx = x * spacing + offset [0]
            self.Add (Line ((lx, offset [1]),
                            (lx, offset [1] + size [1] * spacing),
                            stroke=stroke))

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

class SvgVisitor (Visitor):
    def __init__ (self, filename):
        self._filename = filename

    def VisitElement (self, element, ctx = None):
        c = element.GetChildren ()
        if len (c) == 0:
            return None
        else:
            g = ctx.g ()
            for e in c:
                svgItem = self.VisitGeneric (e, ctx)

                if svgItem is None:
                    continue

                if (e.GetScale ()[0] != 1 or e.GetScale ()[1] != 1):
                    svgItem.scale (e.GetScale ())

                g.add (svgItem)

            return g

    def VisitLine (self, line, ctx = None):
        p = dict ()
        p.update (self._SvgStroke (line.GetStroke ()))

        return ctx.line (line.GetStart (), line.GetEnd (),
            **p)

    def VisitPolygon (self, polygon, ctx = None):
        p = dict ()
        p.update (self._SvgStroke (polygon.GetStroke ()))
        p ['fill'] = self._SvgFill (polygon.GetFill ())

        return ctx.polygon (polygon.GetPoints (),
            **p)

    def VisitRectangle (self, rectangle, ctx=None):
        p = dict ()
        p.update (self._SvgStroke (rectangle.GetStroke ()))
        p ['fill'] = self._SvgFill (rectangle.GetFill ())

        return ctx.rect (rectangle.GetPosition (),
            rectangle.GetSize (),
            **p)

    def Save (self, image):
        d = svgwrite.Drawing (self._filename,
            size = (image.GetWidth (), image.GetHeight ()),
            profile = 'full')

        rootItem = self.VisitGeneric (image, d)

        if rootItem is not None:
            d.add (rootItem)

        d.save ()

    def _SvgStroke (self, stroke):
        if stroke is None:
            return {'stroke' : 'none'}
        else:
            return {'stroke':self._SvgColor (stroke.GetColor ()),
                    'stroke_width' : stroke.GetWidth (),
                    'stroke_linejoin' : self._SvgLineJoin (stroke.GetLineJoin ()),
                    'stroke_linecap' : self._SvgLineCap (stroke.GetLineCap ())
                    }

    def _SvgFill (self, fill):
        if fill is None:
            return 'none'
        else:
            return self._SvgColor (fill.GetColor ())

    def _SvgColor (self, color):
        return svgwrite.rgb (color.R (), color.G (), color.B ())

    def _SvgLineJoin (self, lineJoin):
        m = {
            LineJoin.Round : 'round',
            LineJoin.Miter : 'miter',
            LineJoin.Bevel : 'bevel'
        }

        return m [lineJoin]

    def _SvgLineCap (self, lineCap):
        m = {
            LineCap.Butt : 'butt',
            LineCap.Round : 'round',
            LineCap.Square : 'square'
        }

        return m [lineCap]
