import unittest
from luna.geo import Vector2

class TestVector2 (unittest.TestCase):
	def test_Add (self):
		a = Vector2 (1, 2)
		b = Vector2 (3, 4)
		r = a + b

		self.assertEqual (r.x, 4)
		self.assertEqual (r.y, 6)

if __name__=='__main__':
	unittest.main ()
