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

## Instalação do Antlr
Obtenha o Antlr4 de alguma fonte. Note que o ambiente já existe. O comando
abaixo vai gerar o mesmo ambiente novamente.

# Como gerar o ambiente
```bash
antlr4 -Dlanguage=Python3 -no-listener -visitor LA.g4
```

# Execução do programa
```bash
./run.sh entrada.txt saida.txt
```

# Sobre o Projeto
Temos alguns arquivos principais: [main.py](main.py), [LA.g4](LA.g4),
[LALexer.py](LALexer.py) [LAParser.py](LAParser.py).


O [LA.g4](LA.g4) possui todas as regras para a gramática LA, temos
palavras-chaves, cadeia de carácteres, números inteiros, números reais,
variaveis e espaços em branco.

A partir desse arquivo utilizamos Antlr4 para gerar [LA.py](LA.py) que
implementa um *Parser* LA com as regras dadas.

Na [main.py](main.py) instanciamos um Parser LA e o utilizamos para ler o
arquivo dado como entrada. Com isso, conseguimos todos os tokens possíveis até
que haja algum erro ou chegue no fim do arquivo.

Ainda na [main.py](main.py) definimos dois `ErrorListener`s que é responsável
por diferenciar e levantar os erros que serão pegos na main e posteriormente
escritos no arquivo de saida.


