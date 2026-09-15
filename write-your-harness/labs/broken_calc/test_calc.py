import unittest

from calc import add, mul


class CalcTests(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(2, 3), 5)

    def test_mul(self):
        self.assertEqual(mul(4, 5), 20)


if __name__ == "__main__":
    unittest.main()
