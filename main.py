import sys
from antlr4 import *
from LA import LA


def main(argv):
    input_stream = FileStream(argv[1])
    lexer = LA(input_stream)
    
    t = lexer.nextToken()

    while t.type != -1:
        if t.type == 1: 
            print(f'<\'{t.text}\',\'{t.text}\'>')
        elif t.type != 5 and t.type != 3:
            print(f'<\'{t.text}\',{LA.symbolicNames[t.type]}>')
        
        t = lexer.nextToken()


if __name__ == '__main__':
    main(sys.argv)

