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
    def __init__(self, identifier=None):
        self._scale = (1, 1)
        self._children = []
        self._shared = []
        if identifier is None:
            self._id = self.__class__.__name__ + '|' + str(id(self))
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
    def __init__(self, name=None):
        super(Group, self).__init__ ()
        self._name = name

    def Add (self, item):
        self._children.append (item)

class Drawing (Group):
    def __init__(self, width, height, margin = 4):
        '''Create a new drawing.

        Margin sets a margin around the drawing and thus increases the actual
        size. This is useful if a rectangle is drawn around the whole image;
        without the margin, parts of the line might be cut off.'''
        super(Drawing, self).__init__ ()
        self._width = width
        self._height = height
        self._margin = margin

    def GetWidth (self):
        return self._width

    def GetHeight (self):
        return self._height

    def GetMargin (self):
        return self._margin

    def SaveSvg (self, filename):
        v = SvgVisitor (filename)
        v.Save (self)

    def AddShared (self, item):
        '''Add a new, shared element.

        This element will be invisible by default. To place it in the drawing,
        use an Instance which references this object.'''
        self._shared.append (item)

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

class SvgVisitor (Visitor):
    def __init__ (self, filename):
        self._filename = filename

    def _UpdateCommonAttributes (self, svgItem, element):
        if element.IsReferenced ():
            svgItem ['id'] = element.GetId ()

        if (element.GetScale ()[0] != 1 or element.GetScale ()[1] != 1):
            svgItem.scale (e.GetScale ())

    def VisitElement (self, element, ctx = None):
        for s in element.GetShared ():
            svgItem = self.VisitGeneric (s, ctx)

            if svgItem is None:
                continue

            self._UpdateCommonAttributes (svgItem, s)

            ctx.defs.add (svgItem)

        c = element.GetChildren ()
        if len (c) == 0:
            return None
        else:
            g = ctx.g ()
            for e in c:
                svgItem = self.VisitGeneric (e, ctx)

                if svgItem is None:
                    continue

                self._UpdateCommonAttributes (svgItem, e)

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

    def VisitInstance (self, instance, ctx=None):
        return ctx.use ('#' + instance.GetSource().GetId (),
            insert=instance.GetPosition ())

    def Save (self, image):
        d = svgwrite.Drawing (self._filename,
            size = (image.GetWidth () + image.GetMargin () * 2,
                    image.GetHeight () + image.GetMargin () * 2),
            profile = 'full')

        rootItem = self.VisitGeneric (image, d)
        rootItem.translate (image.GetMargin (), image.GetMargin ())
        if rootItem is not None:
            d.add (rootItem)

        d.save ()

    def _SvgStroke (self, stroke):
        if stroke is None:
            return {'stroke':'none'}
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
