import sys
from antlr4 import *
from LA import LA as OLA


class LA(OLA):
    def __init__(self, file, input=None, output = sys.stdout):
        self.file = file
        super().__init__(input, output)

    def notifyListeners(self, e):
        start = self._tokenStartCharIndex
        stop = self._input.index
        text = self._input.getText(start, stop)
        invalidToken = self.getErrorDisplay(text)
        if invalidToken[0] == '{':
            msg = f"Linha {self._tokenStartLine}: comentario nao fechado\n"
        else:
            msg = f"Linha {self._tokenStartLine}: {invalidToken} - simbolo nao identificado\n"
        self.file.write(msg)
        self._hitEOF = True


def main(argv):
    input_stream = FileStream(argv[1], encoding='utf-8')
    f = open(argv[2], "w")
    lexer = LA(f, input_stream)
    t : Lexer = lexer.nextToken()
    while t.type != -1:
        if t.type == 1: 
            f.write(f'<\'{t.text}\',\'{t.text}\'>\n')
        elif LA.symbolicNames[t.type] != 'WS' and LA.symbolicNames[t.type] != 'COMENTARIO':
            f.write(f'<\'{t.text}\',{LA.symbolicNames[t.type]}>\n')
        
        t = lexer.nextToken()
    f.close()


if __name__ == '__main__':
    main(sys.argv)

