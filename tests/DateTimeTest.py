import unittest
from datetime import datetime


class MyTestCase(unittest.TestCase):
    def test_something(self):
        d = datetime.today().timestamp()
        print(d)
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
