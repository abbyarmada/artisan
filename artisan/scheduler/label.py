__all__ = [
    "Label",
    "LabelExpr"
]


class _LabelExprOperator(object):
    def __init__(self, string):
        self.string = string

    def __str__(self):
        return " %s " % self.string

    def apply(self, left, right=None):
        raise NotImplementedError()


class _LabelOperatorAnd(_LabelExprOperator):
    def __init__(self):
        super(_LabelOperatorAnd, self).__init__("&")

    def apply(self, left, right=None):
        return left and right


class _LabelOperatorOr(_LabelExprOperator):
    def __init__(self):
        super(_LabelOperatorOr, self).__init__("|")

    def apply(self, left, right=None):
        return left or right


class _LabelOperatorNot(_LabelExprOperator):
    def __init__(self):
        super(_LabelOperatorNot, self).__init__("~")

    def __str__(self):
        return "%s" % self.string

    def apply(self, _, right=None):
        return not right


class LabelExpr(object):
    def __init__(self, left_label, right_label=None, operator=None):
        if right_label and not operator:
            raise ValueError("right_label and operator must be given together.")
        self.left_label = left_label
        self.right_label = right_label
        self.operator = operator

    def matches(self, labels):
        if isinstance(self.left_label, LabelExpr):
            left_result = self.left_label.matches(labels)
        else:
            left_result = None
        if isinstance(self.right_label, LabelExpr):
            right_result = self.right_label.matches(labels)
        else:
            right_result = None
        if self.operator:
            result = self.operator.apply(left_result, right_result)
        else:
            if left_result is None:
                result = right_result
            else:
                result = left_result
        return bool(result)

    def __and__(self, other):
        assert isinstance(other, LabelExpr)
        return LabelExpr(self, other, _LabelOperatorAnd())

    def __or__(self, other):
        assert isinstance(other, LabelExpr)
        return LabelExpr(self, other, _LabelOperatorOr())

    def __invert__(self):
        return LabelExpr(None, self, _LabelOperatorNot())

    def __str__(self):
        if self.left_label and self.right_label:
            return "([%s]%s[%s])" % (self.left_label, self.operator, self.right_label)
        elif self.right_label:
            if self.operator:
                return "%s[%s]" % (self.operator, self.right_label)
            return "%s" % self.right_label
        elif self.left_label:
            return "%s" % self.left_label

    def __repr__(self):
        return "<LabelExpr left=%s operator=%s right=%s>" % (repr(self.left_label),
                                                             str(self.operator),
                                                             repr(self.right_label))


class Label(LabelExpr):
    def __init__(self, label):
        self.label = label
        super(Label, self).__init__(None)

    def matches(self, labels):
        return self.label in labels

    def __str__(self):
        return self.label
