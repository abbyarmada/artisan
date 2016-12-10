import sys
from artisan.scheduler import Label, LabelExpr, string_to_label_expr

if sys.version_info >= (2, 7):
    import unittest
else:
    import unittest2 as unittest


class TestLabelExpr(unittest.TestCase):
    def test_simple_label(self):
        label1 = Label("1")
        label2 = Label("2")

        self.assertEqual(str(label1), "1")

        self.assertTrue(label1.matches(["1", "3"]))
        self.assertFalse(label2.matches(["1", "3"]))

    def test_not_operator(self):
        label_expr = ~Label("1")

        self.assertEqual(str(label_expr), "~[1]")

        self.assertIsInstance(label_expr, LabelExpr)
        self.assertTrue(label_expr.matches([]))
        self.assertTrue(label_expr.matches(["2"]))
        self.assertFalse(label_expr.matches(["1"]))

    def test_and_operator(self):
        label_expr = (Label("1") & Label("2"))

        self.assertEqual(str(label_expr), "([1] & [2])")

        self.assertIsInstance(label_expr, LabelExpr)
        self.assertFalse(label_expr.matches(["1"]))
        self.assertFalse(label_expr.matches(["2"]))
        self.assertTrue(label_expr.matches(["1", "2"]))

    def test_or_operator(self):
        label_expr = (Label("1") | Label("2"))

        self.assertEqual(str(label_expr), "([1] | [2])")

        self.assertIsInstance(label_expr, LabelExpr)
        self.assertFalse(label_expr.matches([]))
        self.assertTrue(label_expr.matches(["1"]))
        self.assertTrue(label_expr.matches(["2"]))
        self.assertTrue(label_expr.matches(["1", "2"]))
        self.assertFalse(label_expr.matches(["3", "4"]))

    def test_no_operator(self):
        self.assertRaises(ValueError, lambda: LabelExpr(Label("1"), Label("2")))

    def test_label_equals(self):
        self.assertEqual(Label("1"), Label("1"))
        self.assertNotEqual(Label("1"), Label("2"))

    def test_label_matches(self):
        label_expr = (Label("1") | Label("2"))
        self.assertTrue(label_expr.matches([Label("0"), Label("1")]))
        self.assertFalse(label_expr.matches([Label("0"), Label("3")]))

    def test_label_expr_equal(self):
        data = [Label("abc"),
                ~Label("abc"),
                Label("abc") | Label("def"),
                Label("abc") & Label("def"),
                Label("abc") | (Label("def") & ~Label("ghi"))]

        for label_expr in data:
            self.assertTrue(label_expr == label_expr)
