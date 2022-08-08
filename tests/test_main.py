import os
from antlr4 import *
from T1.LALexer import LALexer
from T1.LAParser import LAParser
from T1.LASemantico import LASemantico

for path in os.listdir('./tests/data/'):
    print(path)
    infile = FileStream('./tests/data/' + path, encoding='utf-8')
    lexer = LALexer(infile)
    stream = CommonTokenStream(lexer)
    parser = LAParser(stream)
    listener = LASemantico()
    parser.addParseListener(listener)
    parser.programa()
