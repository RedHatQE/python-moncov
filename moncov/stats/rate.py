import fractions

class Rate(fractions.Fraction):

    def __new__(cls, numerator=0, denominator=None):
        '''avoid reduction'''
        self = super(Rate, cls).__new__(cls, numerator, denominator)
        if denominator is None:
            return self
        gcd = fractions.gcd(numerator, denominator)
        self._numerator *= gcd
        self._denominator *= gcd
        return self

    def __or__(self, other):
        '''grow the portion and the pie size'''
        return type(self)(self.numerator + other.numerator,
                        self.denominator + other.denominator)

    def __repr__(self):
        return '%s(%r, %r)' % (type(self).__name__, self.numerator, self.denominator)

    def __str__(self):
        return '%s/%s' % (self.numerator, self.denominator)

    @property
    def fraction(self):
        '''return a fraction created out of a rate instance'''
        return Fraction(self.numerator, self.denominator)


