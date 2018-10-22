import unittest

from pflacs import Loadcase, Parameter


def add_abc(a, b, c=0):
    return a + b + c

def sub_xy(x, y):
    return x - y


basecase = Loadcase("Base case", params={"a":10, "b":20, "c":30},
                data={"description": "This is the base-case loadcase."})
basecase.plugin_func(add_abc)

para1 = Loadcase("Parameter study 1", parent=basecase,
                data={"description": ("This is the 1st parameter study "
                "loadcase, it is effectively the same as the base-case." )
                })
para1.plugin_func(sub_xy, argmap={"x": "a", "y":"b"})

para2 = Loadcase("Parameter study 2", parent=basecase,
                params={"a":-20.8},
                data={"description": ("This is the 2nd parameter study "
                "loadcase." )
                })


print(basecase.to_texttree())

class BasicTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_basecase_add_abc1(self):
        self.assertEqual(basecase.add_abc(), 60)

    def test_basecase_add_abc2(self):
        self.assertEqual(basecase.add_abc(a=100), 150)

    def test_basecase_sub_xy(self):
        self.assertEqual(basecase.sub_xy(), -10)

    def test_para1_add_abc1(self):
        self.assertEqual(para1.add_abc(), 60)

    def test_para1_add_abc2(self):
        self.assertEqual(para1.add_abc(a=100), 150)

    def test_para2_add_abc1(self):
        self.assertEqual(para2.add_abc(), 29.2)

    def test_para2_add_abc2(self):
        self.assertEqual(para2.add_abc(c=-1000), -1000.8)




if __name__ == '__main__':
    unittest.main()


