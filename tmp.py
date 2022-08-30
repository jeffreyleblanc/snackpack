
'''
white AND red:
==============
    text
==============

dark gray text

Blue text

---green----- blue[Syncing] bold[Name] ----green--------

white green white

indented cyan

red

'''

from os import get_terminal_size
import textwrap
import json
from math import floor,ceil

class SnackPrinter:

    def __init__(self):
        s = get_terminal_size()
        self.NCOLS = s.columns
        self.NROWS = s.lines

    def p(self, text):
        print(text)

    def red(self, text):
        print(f"\x1b[31m{text}\x1b[0m")

    def blue(self, text):
        print(f"\x1b[34m{text}\x1b[0m")

    def dblue(self, text):
        print(f"\x1b[38;5;27m{text}\x1b[0m")

    def cyan(self, text):
        print(f"\x1b[36m{text}\x1b[0m")

    def redbold(self, text):
        print(f"\x1b[31;1m{text}\x1b[0m")

    def green(self, text):
        print(f"\x1b[92m{text}\x1b[0m")

    def yellow(self, text):
        # yellow1
        print(f"\x1b[38;5;226m{text}\x1b[0m")

    def gray(self, text):
        # gray30
        print(f"\x1b[38;5;239m{text}\x1b[0m")

    def w(self, text):
        sys.stdout.write(text)

    def w_blue(self, text):
        # dodger_blue2
        self.w(f"\x1b[38;5;27m{text}\x1b[0m")

    def indent(self, text, indent=4):
        return textwrap.indent(text, prefix=' '*indent)

    def hr(self, char='=', newline=False):
        line = char*self.NCOLS
        return ( f'\n{line}\n' if newline else line )

    def center(self, text, pad=None, newline=False):
        tl = len(text)
        n = 0.5 * ( self.NCOLS - tl )
        if pad is None:
            line = f'{" "*floor(n)}{text}{" "*ceil(n)}'
        else:
            n -= 2
            line = f'{pad*floor(n)}  {text}  {pad*ceil(n)}'
        return ( f'\n{line}\n' if newline else line )

    def head(self, text):
        hr = self.hr()
        line = f'{hr}\n{self.center(text)}\n{hr}'
        return f'\n{line}\n'

if __name__ == '__main__':

    P = SnackPrinter()

    P.red('This is some red text')
    P.redbold('This is some red *bold* text')
    P.blue('This is some blue text')
    P.cyan('This is some cyan text')
    P.dblue('This is dodger blue')
    P.gray('This is gray30')
    P.p('This is normal printing')
    P.green('This is green')

    obj = dict(key='value',foo='bar')
    P.cyan(P.indent(json.dumps(obj,indent=4)))

    P.green(P.hr())
    P.blue(P.hr(char='~'))
    P.p(P.center('some nice text'))
    P.green(P.center('some nice text',pad='-'))
    P.blue(P.head('some nice text'))