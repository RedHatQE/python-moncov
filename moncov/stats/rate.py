import fractions

class Rate(fractions.Fraction):

    from distutils.sysconfig import get_python_version
    from distutils.version import LooseVersion

    if get_python_version() <= LooseVersion('2.6'):
        # avoid 2.6 Fraction panicking when denominator is None
        def __new__(cls, numerator=0, denominator=None):
            '''avoid reduction'''
            if denominator is None:
                self = super(Rate, cls).from_float(float(numerator))
                return self
            self = super(Rate, cls).__new__(cls, numerator, denominator)
            gcd = fractions.gcd(numerator, denominator)
            self._numerator *= gcd
            self._denominator *= gcd
            return self
    else:
        def __new__(cls, numerator=0, denominator=None):
            '''avoid reduction'''
            self = super(Rate, cls).__new__(cls, numerator, denominator)
            if denominator is None:
                return self
            gcd = fractions.gcd(numerator, denominator)
            self._numerator *= gcd
            return self

    def __or__(self, other):
        '''grow the portion and the pie size'''
        return type(self)(self.numerator + other.numerator,
                        self.denominator + other.denominator)

    def __and__(self, other):
        '''grow the portion and pie size if both self and other are not zero'''
        if self != 0 and other != 0:
            return self | other
        elif self == 0 and other != 0:
            return other
        elif self !=0 and other == 0:
            return self
        else:
            return Rate(0)

    def __repr__(self):
        return '%s(%r, %r)' % (type(self).__name__, self.numerator, self.denominator)

    def __str__(self):
        return '%s/%s' % (self.numerator, self.denominator)

    @property
    def fraction(self):
        '''return a fraction created out of a rate instance'''
        return Fraction(self.numerator, self.denominator)


