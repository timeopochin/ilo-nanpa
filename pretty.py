from sym import *

# Add brackets to an expression
def brackets(exprH, exprPretty):
    if exprH == 1:
        return ['(' + exprPretty[0] + ')']
    else:
        withBrackets = []
        withBrackets.append('⎛' + exprPretty[0] + '⎞')
        for i in range(1, exprH - 1):
            withBrackets.append('⎜' + exprPretty[i] + '⎟')
        withBrackets.append('⎝' + exprPretty[-1] + '⎠')
        return withBrackets

# Render expression with unicode
def pretty(expr):
    exprType = type(expr)

    # Base case (Number)
    if exprType == Num:
        if expr.hasVal:
            val = str(expr.val)
        else:
            val = ' '
        w = len(val)
        if expr.highlight:
            val = '\x1b[7m' + val + '\x1b[0m'
        return w, 1, 0, [val]

    # Highlight expression if needed
    if expr.highlight:
        expr.highlight = False
        aW, aH, aA, a = pretty(expr)
        new = ['\x1b[7m' + i + '\x1b[0m' for i in a]
        return aW, aH, aA, new

    # Rendered expression
    p = []

    # Get the sub expressions
    aW, aH, aA, a = pretty(expr.a)
    bW, bH, bA, b = pretty(expr.b)

    # Order for brackets in horizontal operators
    order = [Mul, Sub, Add]
    symbols = [' • ', ' - ', ' + ']

    # Horizontal concatenation
    if exprType in order:

        # Set the symbol
        separator = symbols[order.index(exprType)]

        # Add brackets if needed
        if type(expr.a) in order:
            if order.index(type(expr.a)) > order.index(type(expr)):
                a = brackets(aH, a)
                aW += 2
        if type(expr.b) in order:
            if order.index(type(expr.b)) > order.index(type(expr)):
                b = brackets(bH, b)
                bW += 2

        # Calculate the final size
        maxH = max(aH, bH)
        maxA = max(aA, bA)
        maxDrop = max(aH - aA, bH - bA)
        newH = maxA + maxDrop

        # Make both sub expressions the same height
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

        # Concatenate the sub expressions
        for i in range(newH):
            if i == maxA:
                p.append(a[i] + separator + b[i])
            else:
                p.append(a[i] + ' '*len(separator) + b[i])
        return aW + bW + 3, newH, maxA, p

    # Fraction
    elif exprType == Div:

        # Add brackets if needed
        if type(expr.a) == Div:
            a = brackets(aH, a)
            aW += 2
        if type(expr.b) == Div:
            b = brackets(bH, b)
            bW += 2

        # Calculate horizontal offset
        maxW = max(aW, bW)
        aO = (maxW - aW)//2
        bO = (maxW - bW)//2

        # Concatenate the sub expressions
        p += [' '*aO + i + ' '*(maxW - aW - aO) for i in a]
        p.append('─'*maxW)
        p += [' '*bO + i + ' '*(maxW - bW - bO) for i in b]
        return maxW, aH + bH + 1, aH, p

    # Power
    elif exprType == Pow:

        # Add brackets if needed
        if type(expr.a) != Num:
            a = brackets(aH, a)
            aW += 2

        # Concatenate the sub expressions
        p += [' '*aW + i for i in b]
        p += [i + ' '*bW for i in a]
        return aW + bW, aH + bH, bH + aA, p

