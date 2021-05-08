class Num:
    def __init__(self, val):
        self.hasVal = True
        if type(val) != str:
            self.val = val
        elif val not in '_':
            if '.' in val:
                #self.val = float(val)
                self.val = val
            else:
                self.val = int(val)
        else:
            self.val = 0
            self.hasVal = False
        self.highlight = False

    def __repr__(self):
        return f'Num({self.val})'

    def __eq__(self, other):
        if type(other) != type(self):
            return False
        return self.val == other.val

    @property
    def evaluated(self):
        if type(self.val) == int:
            return self
        elif type(self.val) == str and '.' in self.val:
            numerator = int(self.val.replace('.', ''))
            denominator = 10**len(self.val.split('.')[1])
            return Div(numerator, denominator).evaluated
        return self

class Operator:
    def __init__(self, a, b):
        if type(a) == int:
            self.a = Num(a)
        else:
            self.a = a
        if type(b) == int:
            self.b = Num(b)
        else:
            self.b = b
        self.highlight = False

    def __repr__(self):
        return f'{str(type(self))[15:18]}({self.a}, {self.b})'

    def __eq__(self, other):
        if type(other) != type(self):
            return False
        return other.a == self.a and other.b == self.b

class Add(Operator):
    @property
    def evaluated(self):
        a = self.a.evaluated
        b = self.b.evaluated

        if type(a) == Num and type(b) == Num:
            return Num(a.val + b.val).evaluated

        elif type(a) == Div and type(b) == Num:
            return Div(Add(a.a, Mul(a.b, b.val).evaluated).evaluated, a.b).evaluated

        elif type(a) == Num and type(b) == Div:
            return Div(Add(b.a, Mul(b.b, a.val).evaluated).evaluated, b.b).evaluated

        elif type(a) == Div and type(b) == Div:
            return Div(Add(Mul(a.a, b.b).evaluated, Mul(b.a, a.b).evaluated).evaluated, Mul(a.b, b.b).evaluated).evaluated

        return Add(a, b)

class Sub(Add):
    @property
    def evaluated(self):
        a = self.a.evaluated
        b = self.b.evaluated

        if type(a) == Num and type(b) == Num:
            return Num(a.val - b.val).evaluated

        elif type(a) == Div and type(b) == Num:
            return Div(Sub(a.a, Mul(a.b, b.val).evaluated).evaluated, a.b).evaluated

        elif type(a) == Num and type(b) == Div:
            return Div(Sub(b.a, Mul(b.b, a.val).evaluated).evaluated, b.b).evaluated

        elif type(a) == Div and type(b) == Div:
            return Div(Sub(Mul(a.a, b.b).evaluated, Mul(b.a, a.b).evaluated).evaluated, Mul(a.b, b.b).evaluated).evaluated

        return Sub(a, b)

class Mul(Add):
    @property
    def evaluated(self):
        a = self.a.evaluated
        b = self.b.evaluated

        if type(a) == Num and type(b) == Num:
            return Num(a.val*b.val)

        elif type(a) == Div and type(b) == Num:
            return Div(Mul(a.a, b).evaluated, a.b).evaluated

        elif type(a) == Num and type(b) == Div:
            return Div(Mul(b.a, a).evaluated, b.b).evaluated

        elif type(a) == Div and type(b) == Div:
            return Div(Mul(a.a, b.a).evaluated, Mul(a.b, b.b).evaluated).evaluated

        elif type(a) == Pow and type(b) == Pow:
            if a.a == b.a:
                return Pow(a.a, Add(a.b, b.b).evaluated).evaluated

        elif type(a) == Pow and type(b) == Num:
            if a.a == b:
                return Pow(a.a, Add(a.b, 1).evaluated).evaluated

        elif type(a) == Num and type(b) == Pow:
            if a == b.a:
                return Pow(a, Add(1, b.b).evaluated).evaluated

        return Mul(a, b)

class Div(Operator):
    @property
    def evaluated(self):
        a = self.a.evaluated
        b = self.b.evaluated

        if type(a) == Num and type(b) == Num:
            if not b.hasVal:
                b.val = 1
            if not a.val % b.val:
                return Num(a.val//b.val)
            hcf = highestCommonFactor(a.val, b.val)
            newA = a.val//hcf
            newB = b.val//hcf
            return Div(newA, newB)

        elif type(a) == Div and type(b) == Num:
            return Div(a.a, Mul(a.b, b).evaluated).evaluated

        elif type(a) == Num and type(b) == Div:
            return Div(Mul(a, b.b).evaluated, b.a).evaluated

        elif type(a) == Div and type(b) == Div:
            return Div(Mul(a.a, b.b).evaluated, Mul(a.b, b.a).evaluated).evaluated

        return Div(a, b)

class Pow(Operator):
    @property
    def evaluated(self):
        a = self.a.evaluated
        b = self.b.evaluated

        if type(b) == Num and not b.hasVal:
            b.val = 1

        if type(a) == Num and a.val == 1:
            return Num(1)

        elif type(b) == Num and type(b.val) == int:
            if not b.val:
                return Num(1)
            result = a
            for i in range(b.val - 1):
                result = Mul(result, a).evaluated
            return result

        elif type(a) == Pow:
            return Pow(a.a, Mul(a.b, b).evaluated).evaluated

        return Pow(a, b)

class Root(Operator):
    @property
    def evaluated(self):
        return Pow(self.a, Div(1, self.b)).evaluated

def getExprs(inputStack, cursor, ops, opClasses):
    exprs = []
    for i in range(len(inputStack)):
        if inputStack[i] in '_' or inputStack[i].isdigit() or '.' in inputStack[i]:
            exprs.append(Num(inputStack[i]))
        elif inputStack[i] in ops:
            b = exprs.pop()
            a = exprs[-1]
            exprs[-1] = opClasses[ops.index(inputStack[i])](a, b)
        if i == cursor:
            exprs[-1].highlight = True
    return exprs

# Calculate the highest common factor
def highestCommonFactor(a, b):
    while(b):
        a, b = b, a % b
    return a
