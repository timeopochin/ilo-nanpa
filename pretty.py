class Num:
    def __init__(self, val):
        self.hasVal = True
        if type(val) != str:
            self.val = val
        elif val not in '_':
            if '.' in val:
                self.val = float(val)
            else:
                self.val = int(val)
        else:
            self.val = 0
            self.hasVal = False
        self.highlight = False

    def __repr__(self):
        return f'Num({self.val})'

    @property
    def evaluated(self):
        #print('\n'.join(self.prettiest[3]))
        #print('---------------------------')
        return self

    @property
    def prettiest(self):
        if self.hasVal:
            val = str(self.val)
        else:
            val = ' '
        w = len(val)
        if self.highlight:
            val = '\x1b[7m' + val + '\x1b[0m'
        return w, 1, 0, [val]

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

    @property
    def prettiest(self):
        aW, aH, aA, a = self.pretty
        new = ['\x1b[7m' + i + '\x1b[0m' if self.highlight else i for i in a]
        return aW, aH, aA, new

    @staticmethod
    def brackets(a):
        if len(a) == 1:
            return ['(' + a[0] + ')']
        else:
            new = []
            new.append('⎛' + a[0] + '⎞')
            for i in range(1, len(a) - 1):
                new.append('⎜' + a[i] + '⎟')
            new.append('⎝' + a[-1] + '⎠')
            return new

class Add(Operator):
    def __init__(self, a, b):
        super(Add, self).__init__(a, b)
        self.separator = ' + '

    @property
    def evaluated(self):
        #print('\n'.join(self.prettiest[3]))
        #print('---------------------------')
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

        #else:
            #print(f'Need to implement {type(a)} {type(b)} for {type(self)}')
            #print()

        return Add(a, b)

    @property
    def pretty(self):
        p = []
        aW, aH, aA, a = self.a.prettiest
        bW, bH, bA, b = self.b.prettiest
        maxH = max(aH, bH)
        maxA = max(aA, bA)

        order = [Mul, Sub, Add]

        if type(self.a) in order:
            if order.index(type(self.a)) > order.index(type(self)):
                a = Operator.brackets(a)
                aW += 2

        if type(self.b) in order:
            if order.index(type(self.b)) > order.index(type(self)):
                b = Operator.brackets(b)
                bW += 2

        maxDrop = max(aH - aA, bH - bA)
        newH = maxA + maxDrop

        while aH < newH:
            if aA < maxA:
                a.insert(0, ' '*aW)
                aA += 1
            else:
                a.append(' '*aW)
            aH += 1

        while bH < newH:
            if bA < maxA:
                b.insert(0, ' '*bW)
                bA += 1
            else:
                b.append(' '*bW)
            bH += 1

        for i in range(newH):
            if i == maxA:
                p.append(a[i] + self.separator + b[i])
            else:
                p.append(a[i] + '   ' + b[i])

        return aW + bW + 3, newH, maxA, p

class Sub(Add):
    def __init__(self, a, b):
        super(Sub, self).__init__(a, b)
        self.separator = ' - '

class Mul(Add):
    def __init__(self, a, b):
        super(Mul, self).__init__(a, b)
        self.separator = ' • '

    @property
    def evaluated(self):
        #print('\n'.join(self.prettiest[3]))
        #print('---------------------------')
        a = self.a.evaluated
        b = self.b.evaluated

        if type(a) == Num and type(b) == Num:
            return Num(a.val*b.val)

        elif type(a) == Div and type(b) == Num:
            return Div(Mul(a.a, b).evaluated, a.b).evaluated

        elif type(a) == Num and type(b) == Div:
            return Div(Mul(b.a, a).evaluated, b.b).evaluated

        #else:
            #print(f'Need to implement {type(a)} {type(b)} for {type(self)}')
            #print()

class Div(Operator):
    @property
    def evaluated(self):
        #print('\n'.join(self.prettiest[3]))
        #print('---------------------------')
        a = self.a.evaluated
        b = self.b.evaluated

        if type(a) == Num and type(b) == Num:
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

        #else:
            #print(f'Need to implement {type(a)} {type(b)} for {type(self)}')
            #print()

    @property
    def pretty(self):
        p = []
        aW, aH, aA, a = self.a.prettiest
        bW, bH, bA, b = self.b.prettiest

        if type(self.a) == Div:
            a = Operator.brackets(a)
            aW += 2

        if type(self.b) == Div:
            b = Operator.brackets(b)
            bW += 2

        maxW = max(aW, bW)
        aO = (maxW - aW)//2
        bO = (maxW - bW)//2

        p += [' '*aO + i + ' '*(maxW - aW - aO) for i in a]
        p.append('─'*maxW)
        p += [' '*bO + i + ' '*(maxW - bW - bO) for i in b]

        return maxW, aH + bH + 1, aH, p

class Pow(Operator):
    @property
    def pretty(self):
        p = []
        aW, aH, aA, a = self.a.prettiest
        bW, bH, bA, b = self.b.prettiest

        if type(self.a) != Num:
            a = Operator.brackets(a)
            aW += 2

        p += [' '*aW + i for i in b]
        p += [i + ' '*bW for i in a]

        return aW + bW, aH + bH, bH + aA, p

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

def highestCommonFactor(a, b):
    hcf = 1
    for i in range(1, min(a, b) + 1):
        if a % i == 0 and b % i == 0:
            hcf = i
    return hcf
