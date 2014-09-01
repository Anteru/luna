import cairocffi as cairo
from .. import Visitor, LineJoin, LineCap

class CairoVisitor (Visitor):
	def __init__ (self):
		super(CairoVisitor,self).__init__ ()

	def _VisitCompoundElement (self, element, ctx=None):
		c = element.GetChildren ()
		if len (c) == 0:
			return None
		else:
			for e in c:
				self.VisitGeneric (e, ctx)

	def VisitElement (self, element, ctx=None):
		return self._VisitCompoundElement (element, ctx)

	def VisitGroup (self, group, ctx=None):
		if group.GetTranslation () [0] != 0 or group.GetTranslation () [1] != 0:
			ctx.translate (group.GetTranslation () [0],
						group.GetTranslation () [1])

		self._VisitCompoundElement (group, ctx)

		if group.GetTranslation () [0] != 0 or group.GetTranslation () [1] != 0:
			ctx.translate (-group.GetTranslation () [0],
						-group.GetTranslation () [1])

	def VisitLine (self, line, ctx = None):
		if line.GetStroke () is None:
			return

		self._ApplyStroke (line.GetStroke (), ctx)
		ctx.move_to (line.GetStart () [0], line.GetStart () [1])
		ctx.line_to (line.GetEnd () [0], line.GetEnd () [1])
		ctx.stroke ()

	def VisitText (self, text, ctx=None):
		ctx.set_font_size (text.GetFont ().GetSize ())

		if text.GetFont ().GetFontFace () is not None:
			ctx.select_font_face (text.GetFont ().GetFontFace (),
				cairo.FONT_SLANT_NORMAL,
				cairo.FONT_WEIGHT_NORMAL)

		if text.GetFont ().GetFill () is not None:
			self._ApplyFill (text.GetFont ().GetFill (), ctx)

		if text.GetFont ().GetStroke () is not None:
			self._ApplyStroke (text.GetFont ().GetStroke (), ctx)

		ctx.move_to (text.GetPosition ().x, text.GetPosition ().y)
		ctx.show_text (text.GetText ())
		ctx.new_path ()

	def VisitPolygon (self, polygon, ctx = None):
		if polygon.GetFill () is None and polygon.GetStroke () is None:
			return

		points = polygon.GetPoints ()

		if len(points) <= 1:
			return

		ctx.move_to (points [0][0], points [0][1])
		for p in points [1:]:
			ctx.line_to (p [0], p [1])
		ctx.close_path ()

		if polygon.GetFill () is not None:
			self._ApplyFill (polygon.GetFill (), ctx)
			ctx.fill_preserve ()

		if polygon.GetStroke () is not None:
			self._ApplyStroke (polygon.GetStroke (), ctx)
			ctx.stroke_preserve ()

		ctx.new_path ()

	def VisitRectangle (self, rectangle, ctx=None):
		import math
		if rectangle.GetFill () is None and rectangle.GetStroke () is None:
			return

		if rectangle.GetCornerRadius () == 0:
			ctx.rectangle (rectangle.GetPosition () [0], rectangle.GetPosition () [1],
				rectangle.GetSize ().x, rectangle.GetSize ().y)
		else:
			p = rectangle.GetPosition ()
			s = rectangle.GetSize ()
			r = rectangle.GetCornerRadius ()
			# http://cairographics.org/samples/rounded_rectangle/
			ctx.arc (p.x + s.x - r, p.y + r, r, math.radians (-90), math.radians (0))
			ctx.arc (p.x + s.x - r, p.y + s.y - r, r, math.radians (0), math.radians (90))
			ctx.arc (p.x + r, p.y + s.y - r, r, math.radians (90), math.radians (180))
			ctx.arc (p.x + r, p.y + r, r, math.radians (180), math.radians (270))
			ctx.close_path ()

		if rectangle.GetFill () is not None:
			self._ApplyFill (rectangle.GetFill (), ctx)
			ctx.fill_preserve ()

		if rectangle.GetStroke () is not None:
			self._ApplyStroke (rectangle.GetStroke (), ctx)
			ctx.stroke_preserve ()

		ctx.new_path ()

	def VisitCircle (self, circle, ctx=None):
		if circle.GetFill () is None and circle.GetStroke () is None:
			return

		import math

		ctx.arc (circle.GetCenter () [0], circle.GetCenter () [1],
			circle.GetRadius (), 0, 2 * math.pi)

		if circle.GetFill () is not None:
			self._ApplyFill (circle.GetFill (), ctx)
			ctx.fill_preserve ()

		if circle.GetStroke () is not None:
			self._ApplyStroke (circle.GetStroke (), ctx)
			ctx.stroke_preserve ()

		ctx.new_path ()

	def VisitInstance (self, instance, ctx=None):
		ctx.translate (instance.GetPosition () [0], instance.GetPosition () [1])
		self.VisitGeneric (instance.GetSource (), ctx)
		ctx.translate (-instance.GetPosition () [0], -instance.GetPosition () [1])

	def _Render (self, image, surface):
		ctx = cairo.Context (surface)

		ctx.translate (image.GetMargin (), image.GetMargin ())
		self.VisitGeneric (image, ctx)

		return surface

	def SavePng (self, filename, image):
		imageSize = [int(i) for i in image.GetSize ()]
		surface = cairo.ImageSurface (cairo.FORMAT_ARGB32,
			imageSize [0] + image.GetMargin () * 2,
			imageSize [1] + image.GetMargin () * 2)

		self._Render (image, surface).write_to_png (filename)

	def SavePdf (self, filename, image):
		imageSize = [int(i) for i in image.GetSize ()]
		surface = cairo.PDFSurface (filename,
			imageSize [0] + image.GetMargin () * 2,
			imageSize [1] + image.GetMargin () * 2)

		self._Render (image, surface)

	def _ApplyStroke (self, stroke, ctx):
		ctx.set_line_width (stroke.GetWidth ())
		ctx.set_line_join (self._CairoLineJoin (stroke.GetLineJoin ()))
		ctx.set_line_cap (self._CairoLineCap (stroke.GetLineCap ()))

		if stroke.GetDashPattern () is not None:
			ctx.set_dash (stroke.GetDashPattern ())
		else:
			ctx.set_dash ([])

		ctx.set_source_rgba (
			stroke.GetColor ().R () / 255,
			stroke.GetColor ().G () / 255,
			stroke.GetColor ().B () / 255,
			stroke.GetOpacity ())

	def _ApplyFill (self, fill, ctx):
		ctx.set_source_rgba (
			fill.GetColor ().R () / 255,
			fill.GetColor ().G () / 255,
			fill.GetColor ().B () / 255,
			fill.GetOpacity ())

	def _CairoLineJoin (self, lineJoin):
		m = {
			LineJoin.Round : cairo.LINE_JOIN_ROUND,
			LineJoin.Miter : cairo.LINE_JOIN_MITER,
			LineJoin.Bevel : cairo.LINE_JOIN_BEVEL
		}

		return m [lineJoin]

	def _CairoLineCap (self, lineCap):
		m = {
			LineCap.Butt    : cairo.LINE_CAP_BUTT,
			LineCap.Round   : cairo.LINE_CAP_ROUND,
			LineCap.Square  : cairo.LINE_CAP_SQUARE
		}

		return m [lineCap]
