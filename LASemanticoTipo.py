from dataclasses import dataclass
from typing import Dict, List

# A classe Tipo representa um tipo.
class Tipo:
    pass

# O tipo 'Literal' representa uma cadeia de caracteres.
# NOTA: Não confundir com a definição popular de 'literal', de um valor de algum
# tipo expresso diretamente no código fonte.
class Literal(Tipo):
    pass

# O tipo inteiro representa um número inteiro.
# NOTA: A especificação não define a precisão da aritmética inteira.
class Inteiro(Tipo):
    pass

# O tipo real representa um número real.
# NOTA: A especificação não define a implementação da aritmética real.
class Real(Tipo):
    pass

# O tipo lógico é o tipo com dois valores: 'verdadeiro' e 'falso'.
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

# O tipo registro representa um registro.
class Registro(Tipo):
    campos: Dict[str, Tipo]

# O tipo função representa uma função ou um procedimento.
# Procedimentos são funções com tipo de saida Void.
class Função(Tipo):
    entrada: List[Tipo]
    saída: Tipo

# O tipo Void é o tipo sem valor. É um erro semântico atribuí-lo.
class Void(Tipo):
    pass


# Um erro na resolução de apelido de tipo.
class TypeResolutionError(Exception):
    pass


# As funções walk_* descem manualmente uma árvore de tipo para obter a descrição
# estrutural de um tipo.

def walk_tipo_basico(ts, ctx):
    if ctx.getText() == 'literal':
        return Literal
    elif ctx.getText() == 'inteiro':
        return Inteiro
    elif ctx.getText() == 'real':
        return Real
    elif ctx.getText() == 'logico':
        return Lógico

def walk_tipo_basico_ident(ts, ctx):
    if tipo_basico := ctx.tipo_basico():
        return walk_tipo_basico(ts, tipo_basico)
    elif ty := ts.get(ctx.IDENT().getText()):
        return ty
    else:
        line = ctx.IDENT().symbol.line
        tstr = ctx.IDENT().getText()
        raise TypeResolutionError(f'Linha {line}: tipo {tstr} nao declarado')

def walk_tipo_estendido(ts, ctx):
    if ctx.getText()[:1] == '^': # TODO Não sei se essa é a melhor ideia.
        return Ponteiro(walk_tipo_basico_ident(ts, ctx.tipo_basico_ident()))
    else:
        return walk_tipo_basico_ident(ts, ctx.tipo_basico_ident())

def backwalk_dimensao(ty, ctx):
    for exp_aritmetica in ctx.exp_aritmetica:
        # TODO Resolver a dimensão.
        pass
    return ty

def walk_registro(ts, ctx):
    campos = {}
    for variavel in ctx.variavel():
        for identificador in variavel.identificador():
            if len(identificador.IDENT()) > 1:
                raise Exception("eu não sei o que fazer nesse caso")
            ident = identificador.IDENT()[0].getText()
            tipo = identificador.tipo()
            tipo = backwalk_dimensao(tipo, identificador.dimensao())
            if ident in campos:
                raise Exception("campo de registro repetido")
            campos[ident] = tipo
    return Registro(campos)

def walk_tipo(ts, ctx):
    if registro := ctx.registro():
        return walk_registro(ts, registro)
    elif tipo_estendido := ctx.tipo_estendido():
        return walk_tipo_estendido(ts, tipo_estendido)
