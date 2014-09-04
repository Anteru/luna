from luna.geo import Vector2, BoundingBox

def test_Vector2_Add ():
	a = Vector2 (1, 2)
	b = Vector2 (3, 4)
	r = a + b

	assert (r.x == 4)
	assert (r.y == 6)

def test_Vector2_MultiplyScalar ():
	a = Vector2 (3, 5)
	b = a * 3

	assert (b.x == 9)
	assert (b.y == 15)

def test_Vector2_DivideScalar ():
	a = Vector2 (9, 15)
	b = a / 3

	assert (b.x == 3)
	assert (b.y == 5)

def test_BoundingBox_FromPoints ():
	b = BoundingBox.FromPoints ([(5,2), (7, 1), (6, 3)])

	assert (b.GetSize ().x == 2)
