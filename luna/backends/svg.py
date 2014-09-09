import svgwrite
from .. import Visitor, LineJoin, LineCap

class SvgVisitor (Visitor):
	def __init__ (self):
		super(SvgVisitor,self).__init__ ()

	def _UpdateCommonAttributes (self, svgItem, element):
		if element.IsReferenced ():
			svgItem ['id'] = element.GetId ()

		if (element.GetScale ()[0] != 1 or element.GetScale ()[1] != 1):
			svgItem.scale (e.GetScale ())

	def _VisitCompoundElement (self, element, ctx=None):
		for sharedElement in element.GetShared ():
			svgItem = self.VisitGeneric (sharedElement, ctx)
			self._UpdateCommonAttributes (svgItem, sharedElement)

			ctx.defs.add (svgItem)

		children = element.GetChildren ()
		if len (children) == 0:
			return None
		else:
			g = ctx.g ()
			for childElement in children:
				svgItem = self.VisitGeneric (childElement, ctx)
				self._UpdateCommonAttributes (svgItem, childElement)

				g.add (svgItem)

			return g

	def VisitElement (self, element, ctx=None):
		return self._VisitCompoundElement (element, ctx)

	def VisitGroup (self, group, ctx=None):
		g = self._VisitCompoundElement (group, ctx)

		if group.GetTranslation () [0] != 0 or group.GetTranslation () [1] != 0:
			g.translate (group.GetTranslation () [0],
						group.GetTranslation () [1])
		return g

	def VisitLine (self, line, ctx = None):
		p = dict ()
		p.update (self._SvgStroke (line.GetStroke ()))

		return ctx.line (line.GetStart (), line.GetEnd (),
			**p)

	def VisitPolygon (self, polygon, ctx = None):
		p = dict ()
		p.update (self._SvgStroke (polygon.GetStroke ()))
		p.update (self._SvgFill (polygon.GetFill ()))

		return ctx.polygon (polygon.GetPoints (),
			**p)

	def VisitRectangle (self, rectangle, ctx=None):
		p = dict ()
		p.update (self._SvgStroke (rectangle.GetStroke ()))
		p.update (self._SvgFill (rectangle.GetFill ()))

		if rectangle.GetCornerRadius () != 0:
			p ['rx'] = rectangle.GetCornerRadius ()
			p ['ry'] = rectangle.GetCornerRadius ()

		return ctx.rect (rectangle.GetPosition (),
			rectangle.GetSize (),
			**p)

	def VisitImage (self, image, ctx=None):
		p = dict ()

		return ctx.image (image.GetFilename (), image.GetPosition (),
			image.GetSize (), **p) 

	def VisitCircle (self, circle, ctx=None):
		p = dict ()
		p.update (self._SvgStroke (circle.GetStroke ()))
		p.update (self._SvgFill (circle.GetFill ()))

		return ctx.circle (circle.GetCenter (),
			circle.GetRadius (),
			**p)

	def VisitText (self, text, ctx=None):
		p = dict ()

		style = []
		if text.GetFont ().GetFontFace () is not None:
			style.append ('font-face:{};'.format (text.GetFont ().GetFontFace ()))

		style.append ('font-size:{}px;'.format (text.GetFont ().GetSize ()))

		p ['style'] = ''.join (style)

		return ctx.text (text.GetText (), text.GetPosition (), **p)

	def VisitInstance (self, instance, ctx=None):
		return ctx.use ('#' + instance.GetSource().GetId (),
			insert=instance.GetPosition ())

	def Save (self, filename, image):
		imageSize = image.GetSize ()
		print (imageSize [0], image.GetMargin ())
		d = svgwrite.Drawing (filename,
			size = (imageSize [0] + image.GetMargin () * 2,
					imageSize [1] + image.GetMargin () * 2),
			profile = 'full')

		rootItem = self.VisitGeneric (image, d)
		rootItem.translate (image.GetMargin (), image.GetMargin ())
		if rootItem is not None:
			d.add (rootItem)

		d.save ()

	def _SvgStroke (self, stroke):
		if stroke is None:
			return {'stroke' : 'none'}
		else:
			result = {'stroke'          : self._SvgColor (stroke.GetColor ()),
					'stroke_width'      : stroke.GetWidth (),
					'stroke_linejoin'   : self._SvgLineJoin (stroke.GetLineJoin ()),
					'stroke_linecap'    : self._SvgLineCap (stroke.GetLineCap ())
					}

			if stroke.GetDashPattern () is not None:
				result ['stroke-dasharray'] = ','.join (map (str, stroke.GetDashPattern ()))

			if stroke.GetOpacity () != 1:
				result ['stroke_opacity'] = stroke.GetOpacity ()

			return result

	def _SvgFill (self, fill):
		if fill is None:
			return {'fill' :'none'}
		else:
			result = {
				'fill' : self._SvgColor (fill.GetColor ())
			}

			if fill.GetOpacity () != 1:
				result ['fill_opacity'] = fill.GetOpacity ()

			return result

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
