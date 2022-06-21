# Alunos e RAs

- Matheus Ramos de Carvalho 769703
- Miguel Antonio de Oliveira 772180

# Requisitos

- Python 3.8 ou superior
- Antlr 4.10


# Ambiente virtual

## Instalação e criação do virtualenv
```bash
    pip install virtualenv
    virtualenv .venv
```
## Ativando o ambiente virtual
### Windows
```bash
    source .venv/Scripts/activate
```
### Linux
```bash
    source .venv/bin/activate
```

# Instalando dependências
```bash
    pip install -r requirements.txt
```

# Execução do programa
```bash
    ./run.sh entrada.txt saida.txt
```

# Sobre o Projeto
Temos três arquivos principais: [main.py](main.py), [LA.g4](LA.g4) e [LA.py](LA.py).


O [LA.g4](LA.g4) possui todas as regras lexicas para a gramática LA, temos palavras-chaves, cadeia de carácteres, números inteiros, números reais, variaveis e espaços em branco.

A partir desse arquivo utilizamos Antlr4 para gerar [LA.py](LA.py) que implementa um *Lexer* [LA](LA.py?plain=1#L143) com as regras dadas.


Na [main.py](main.py) instanciamos um Lexer LA e o utilizamos para ler o arquivo dado como entrada.
Com isso, conseguimos todos os tokens possíveis até que haja algum erro ou chegue no fim do arquivo.

Ainda na [main.py](main.py) definimos um [LAErrorListener](main.py?plain=1#L11) que é responsável por diferenciar e levantar os erros lexicos que serão pegos na [main](ain.py?plain=1#L23) e posteriormente escritos no arquivo de saida junto aos tokens lidos anteriormente.


