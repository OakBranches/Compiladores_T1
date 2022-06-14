import sys
from antlr4 import *
from LA import LA


def main(argv):
    input_stream = FileStream(argv[1], encoding='utf-8')
    lexer = LA(input_stream)
    
    t = lexer.nextToken()

    while t.type != -1:
        if t.type == 1: 
            print(f'<\'{t.text}\',\'{t.text}\'>')
        elif LA.symbolicNames[t.type] != 'WS' and LA.symbolicNames[t.type] != 'COMENTARIO':
            print(f'<\'{t.text}\',{LA.symbolicNames[t.type]}>')
        
        t = lexer.nextToken()


if __name__ == '__main__':
    main(sys.argv)

