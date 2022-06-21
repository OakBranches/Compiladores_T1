import sys
from antlr4 import *
from antlr4.error.ErrorListener import ErrorListener
from LA import LA


class LexerError(Exception):
    pass


class LAErrorListener(ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        # Constrói uma exceção a partir do erro e levanta para cima.
        ch = str(e.input)[e.startIndex]
        if ch == '"':
            raise LexerError(f'Linha {line}: cadeia literal nao fechada')
        elif ch == '{':
            raise LexerError(f'Linha {line}: comentario nao fechado')
        else:
            raise LexerError(f'Linha {line}: {ch} - simbolo nao identificado')


def main(argv):
    # Lê os argumentos e os arquivos.
    _, input_path, output_path = argv
    infile = FileStream(input_path, encoding='utf-8')
    outfile = open(output_path, 'w')
    
    # lexer = LA(infile)
    lexer = LA(infile)

    # Remove o tratador padrão.
    lexer.removeErrorListeners()

    # Insere o nosso tratador.
    lexer.addErrorListener(LAErrorListener())

    try:
        # Lê cada token.
        while (t := lexer.nextToken()).type != -1:
            if t.type == 1:
                # Palavra-chave
                outfile.write(f'<\'{t.text}\',\'{t.text}\'>')
            else:
                # Outros
                outfile.write(f'<\'{t.text}\',{LA.symbolicNames[t.type]}>')
            outfile.write('\n')
    except LexerError as e:
        # Reporta o erro no arquivo.
        outfile.write(str(e))
        outfile.write('\n')

    # outfile.close()
    outfile.close()


if __name__ == '__main__':
    main(sys.argv)
