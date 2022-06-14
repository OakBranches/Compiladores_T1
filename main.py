import sys
from antlr4 import *
from LA import LA

def main(argv):
    input_stream = FileStream(argv[1])
    lexer = LA(input_stream)
    
    t = lexer.nextToken()

    while t.type != -1:
        print(t)
        t = lexer.nextToken()


if __name__ == '__main__':
    main(sys.argv)

