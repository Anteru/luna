from luna import *

def testDrawingAutoBounds():
	d = Drawing ()

	triangles = [
		[(1,1), (1.5, 1), (1, 2)],
		[(1, 7), (3, 6), (3, 1)],
		[(5,2), (7, 1), (6, 3)],
		[(5, 5), (7, 6), (5, 7)]
	]

	scale = 32

	for triangle in triangles:
		g = Group ()
		g.Add (Line (geo.Vector2 (triangle [0]) * scale, geo.Vector2 (triangle [1]) * scale))
		g.Add (Line (geo.Vector2 (triangle [1]) * scale, geo.Vector2 (triangle [2]) * scale))
		g.Add (Line (geo.Vector2 (triangle [2]) * scale, geo.Vector2 (triangle [0]) * scale))
		d.Add (g)

	b = d.GetBounds ()

	assert (b.GetMinimum ().x == 31.5)
	assert (b.GetMinimum ().y == 31.5)
	assert (b.GetMaximum ().x == (7 * 32 + 0.5))
	assert (b.GetMaximum ().y == (7 * 32 + 0.5))

	s = d.GetSize ()

	# Size is different from bounds, an image goes from (0,0) to bounds max.
	assert (s.x == b.GetMaximum ().x)
	assert (s.y == b.GetMaximum ().y)
