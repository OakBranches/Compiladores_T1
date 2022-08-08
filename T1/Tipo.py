from typing import Dict, List, Optional, Union
from dataclasses import dataclass


# A classe Tipo representa um tipo.
# O método __eq__ para o Tipo executa uma comparação estrutural:
# - Escalares são iguais se eles forem a mesma classe: inteiro = inteiro.
# - Vetores são iguais se seus elementos forem iguais, mas não seu tamanho.
# - Registros são iguais se todos seus campos forem iguais.
# - Ponteiros são iguais se os tipos onde eles apontam são iguais.
# - Funções são iguais se suas entradas e saídas são iguais.
class Tipo:
    pass

# O tipo 'Literal' representa uma cadeia de caracteres.
# NOTA: Não confundir com a definição popular de 'literal', de um valor de algum
# tipo expresso diretamente no código fonte.
@dataclass
class Literal(Tipo):
    pass

# O tipo inteiro representa um número inteiro.
# NOTA: A especificação não define a precisão da aritmética inteira.
@dataclass
class Inteiro(Tipo):
    valor: Optional[int]

    def __eq__(self, lhs):
        return type(self) == type(lhs)

# O tipo real representa um número real.
# NOTA: A especificação não define a implementação da aritmética real.
@dataclass
class Real(Tipo):
    valor: Optional[float]

    def __eq__(self, lhs):
        return type(self) == type(lhs)

Aritmético = Union[Inteiro, Real]

# O tipo lógico é o tipo com dois valores: 'verdadeiro' e 'falso'.
@dataclass
class Lógico(Tipo):
    pass

# O tipo ponteiro representa um ponteiro para uma variável.
# NOTA: A especificação proíbe ponteiros de ponteiros sintaticamente. Não iremos
#       contestar.
@dataclass
class Ponteiro(Tipo):
    interno: Tipo

# O tipo vetor representa um vetor. Seu tamanho deve ser conhecido em tempo de
# compilação.
# NOTA: A especificação não proíbe declaração de vetores de tamanho desconhecido
#       porém iremos ignorar pois isso não faz nenhum sentido.
@dataclass
class Vetor(Tipo):
    interno: Tipo
    tamanho: int

    def __eq__(self, lhs):
        return isinstance(lhs, Vetor) and self.interno == lhs.interno

# O tipo registro representa um registro.
@dataclass
class Registro(Tipo):
    campos: Dict[str, Tipo]

# O tipo função representa uma função ou um procedimento.
# Procedimentos são funções com tipo de saida Void.
@dataclass
class Função(Tipo):
    entrada: List[Tipo]
    saída: Tipo

# O tipo Void é o tipo sem valor. É um erro semântico atribuí-lo.
@dataclass
class Void(Tipo):
    pass
