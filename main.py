import sys
from antlr4 import *
from LA import LA


def main(argv):
    input_stream = FileStream(argv[1], encoding='utf-8')
    lexer = LA(input_stream)
    f = open(argv[2], "w")
    t : Lexer = lexer.nextToken()
    print(argv)
    while t.type != -1:
        if t.type == 1: 
            f.write(f'<\'{t.text}\',\'{t.text}\'>\n')
        elif LA.symbolicNames[t.type] != 'WS' and LA.symbolicNames[t.type] != 'COMENTARIO':
            f.write(f'<\'{t.text}\',{LA.symbolicNames[t.type]}>\n')
        
        t = lexer.nextToken()
    f.close()


if __name__ == '__main__':
    main(sys.argv)

