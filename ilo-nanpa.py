import os
import sys
import tty
import termios
from pretty import *

def write(msg):
    sys.stdout.write(msg.replace('\n', '\n\r'))
    sys.stdout.flush()

def clear():
    write('\x1b[2J')
    goto(1, 1)

def goto(x, y):
    write(f'\x1b[{y};{x}H')

def writeAt(x, y, msg):
    goto(x, y)
    write(msg)

def process(inputStack, char, cursor):

    # Update the input stack
    if char.isdigit():

        # Inputed a number
        if inputStack[cursor[0]] == '_':
            inputStack[cursor[0]] = ''
        if inputStack[cursor[0]].isdigit() or '.' in inputStack[cursor[0]] or not inputStack[cursor[0]]:
            inputStack[cursor[0]] += char
            cursor[1] += 1
        else:
            inputStack.insert(cursor[0] + 1, char)
            cursor[0] += 1
    elif char == '.':

        # Inputed a decimal point
        if inputStack[cursor[0]] == '_':
            inputStack[cursor[0]] = ''
        if inputStack[cursor[0]].isdigit():
            inputStack[cursor[0]] += char
            cursor[1] += 1
        elif not inputStack[cursor[0]]:
            inputStack[cursor[0]] = '0' + char
        else:
            inputStack.insert(cursor[0] + 1, '0' + char)
            cursor[0] += 1
    elif len(inputStack):

        # Clean up empty items
        cleaned = False
        i = len(inputStack)
        while i > 0:
            i -= 1
            if inputStack[i] in '_':
                if inputStack[i] == '_':

                    # Remove the corresponding operator
                    numLeft = 0
                    for j in range(i + 1, len(inputStack)):
                        if inputStack[j].isdigit() or '.' in inputStack[j]:
                            numLeft += 1
                        elif inputStack[j] in OPERATORS:
                            numLeft -= 1
                            if numLeft < 1:
                                del inputStack[j]
                                break
                if len(inputStack) > 1:
                    del inputStack[i]
                    if i <= cursor[0] and cursor[0] > 0:
                        cursor[0] -= 1
                    i -= 1
                    cleaned = True

        # See if an expression is nested
        numLeft = 0
        for i in range(cursor[0] + 1):
            if inputStack[i].isdigit() or '.' in inputStack[i]:
                numLeft += 1
            elif inputStack[i] in OPERATORS:
                numLeft -= 1
        nestedAfter = 0
        for i in range(len(inputStack)):
            if inputStack[i].isdigit() or '.' in inputStack[i]:
                nestedAfter += 1
            elif inputStack[i] in OPERATORS:
                nestedAfter-= 1
        if char in '\r ':

            # Inputed return (or space)
            inputStack.insert(cursor[0] + 1, '')
            cursor[0] += 1
        elif char in OPERATORS:

            # Inputed an operator
            if numLeft >= 2 and (nestedAfter >= 2 or cursor[0] == len(inputStack) - 1):

                # Insert operator
                inputStack.insert(cursor[0] + 1, char)
                cursor[0] += 1
        elif char == '\x7f' and not cleaned:

            # Inputed a backspace
            if len(inputStack[cursor[0]]) == 1 and inputStack[cursor[0]].isdigit():
                inputStack[cursor[0]] = '_'
            else:
                inputStack[cursor[0]] = inputStack[cursor[0]][:-1]
        elif char == 'h' and not cleaned:

            # Inputed left
            if cursor[0] > 0:
                cursor[0] -= 1
        elif char == 'l':

            # Inputde right
            if cursor[0] < len(inputStack) - 1:
                cursor[0] += 1

    # Clean up decimals
    clean = False
    while not clean:
        clean = True
        for i in range(len(inputStack)):
            if inputStack[i] not in '_' and i != cursor[0]:
                if inputStack[i][-1] == '.' or (inputStack[i][-1] == '0' and '.' in inputStack[i]):
                    inputStack[i] = inputStack[i][:-1]
                    clean = False
            elif len(inputStack[i]) > 1 and inputStack[i][0] == '0' and '.' not in inputStack[i]:
                inputStack[i] = inputStack[i][1:]
                clean = False
    
    # Not used fully yet
    cursor[1] = len(inputStack[cursor[0]])

    clear()

    # Print the input stack
    rows, columns = os.popen('stty size', 'r').read().split()
    goto(1, int(rows))
    for i in range(len(inputStack)):
        display = inputStack[i]
        if i == cursor[0]:
            if not display:
                display = ' '
            display = '\x1b[7m' + display + '\x1b[0m'
        display += ' '
        write(display)

    # Print separator
    writeAt(1, int(rows) - 1, '─'*int(columns))

    # Print the rendered stack
    exprs = getExprs(inputStack, cursor[0], OPERATORS, OPCLASSES)
    line = int(rows) - 1
    for exprTree in reversed(exprs):
        exprW, exprH, exprA, expr = exprTree.prettiest
        try:
            evalW, evalH, evalA, eval = exprTree.evaluated.prettiest
            #print(evalW, evalH, evalA, eval)
            #raise
        except:
            evalW = 17
            evalH = 1
            evalA = 0
            eval = ['\x1b[41mNot sovlable yet!\x1b[0m']

        # Colour
        expr = ['\x1b[44m' + i.replace('\x1b[0m', '\x1b[0;44m') + '\x1b[0m' for i in expr]
        eval = ['\x1b[42m' + i.replace('\x1b[0m', '\x1b[0;42m') + '\x1b[0m' for i in eval]

        # Combine
        p = []
        maxH = max(exprH, evalH)
        maxA = max(exprA, evalA)

        maxDrop = max(exprH - exprA, evalH - evalA)
        newH = maxA + maxDrop

        while exprH < newH:
            if exprA < maxA:
                expr.insert(0, ' '*exprW)
                exprA += 1
            else:
                expr.append(' '*exprW)
            exprH += 1

        while evalH < newH:
            if evalA < maxA:
                eval.insert(0, ' '*evalW)
                evalA += 1
            else:
                eval.append(' '*evalW)
            evalH += 1

        for i in range(newH):
            p.append(expr[i] + ' '*(int(columns) - exprW - evalW) + eval[i])

        # Display
        if line - maxH <= 0:
            break
        writeAt(1, line - exprH, '\n'.join(p))
        line -= maxH + 1

OPERATORS = '+-*/^'
OPCLASSES = [Add, Sub, Mul, Div, Pow]

if __name__ == '__main__':

    # Setup raw mode
    fd = sys.stdin.fileno()
    oldSettings = termios.tcgetattr(fd)
    tty.setraw(sys.stdin)

    # Hide the cursor
    write('\x1b[?25l')

    try:
        clear()
        inputStack = ['']

        # [index in stack, index in string]
        cursor = [0, 0]

        # Read input
        process(inputStack, 'l', cursor)
        while True:
            char = sys.stdin.read(1)
            if char == 'q':
                break
            process(inputStack, char, cursor)

    # Avoid breaking the terminal after a crash
    except Exception as e:
        print(e, end = '\n\r')

    # Restore terminal settings
    clear()
    write('\x1b[?25h\n\r')
    termios.tcsetattr(fd, termios.TCSADRAIN, oldSettings)