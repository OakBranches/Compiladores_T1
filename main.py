import sys
from antlr4 import *
from antlr4.error.ErrorListener import ErrorListener
from T1.LALexer import LALexer
from T1.LAParser import LAParser
from T1.LASemantico import LASemantico


class LexerError(Exception):
    pass


class LALexerErrorListener(ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        # Constrói uma exceção a partir do erro e levanta para cima.
        ch = str(e.input)[e.startIndex]
        if ch == '"':
            raise LexerError(f'Linha {line}: cadeia literal nao fechada')
        elif ch == '{':
            raise LexerError(f'Linha {line}: comentario nao fechado')
        else:
            raise LexerError(f'Linha {line}: {ch} - simbolo nao identificado')


class ParserError(Exception):
    pass


class LAParserErrorListener(ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        # Constrói uma exceção a partir do erro e levanta para cima.
        line = offendingSymbol.line
        text = offendingSymbol.text
        if text == '<EOF>':
            text = 'EOF'
        raise ParserError(f'Linha {line}: erro sintatico proximo a {text}')


def main(argv):
    # Lê os argumentos e os arquivos.
    _, input_path, output_path = argv
    infile = FileStream(input_path, encoding='utf-8')
    outfile = open(output_path, 'w')
    
    # Cria o lexer e o parser.
    lexer = LALexer(infile)
    stream = CommonTokenStream(lexer)
    parser = LAParser(stream)

    # Remove os tratadores padrão.
    lexer.removeErrorListeners()
    parser.removeErrorListeners()

    # Insere os nossos tratadores.
    lexer.addErrorListener(LALexerErrorListener())
    parser.addErrorListener(LAParserErrorListener())

    try:
        # Pede para o parser ler um programa.
        visitor = LASemantico()
        visitor.visitPrograma(parser.programa())
        print(visitor.tss)
        # Reporta erros.
        outfile.write('\n'.join(visitor.errors))
        outfile.write('\nFim da compilacao\n')
    except ParserError as e:
        # Reporta o erro no arquivo.
        outfile.write(str(e))
        outfile.write('\nFim da compilacao\n')
    except LexerError as e:
        # Reporta o erro no arquivo.
        outfile.write(str(e))
        outfile.write('\nFim da compilacao\n')

    # Fecha o arquivo de saída.
    outfile.close()


if __name__ == '__main__':
    main(sys.argv)
