from T1.Tipo import *
from T1.TabelaDeSimbolos import TabelaDeSimbolos as TS
from T1.LAParser import LAParser as LA
from T1 import Expr
from typing import List, Tuple


# Um erro na resolução de apelido de tipo.
class TypeResolutionError(Exception):
    pass


# As funções walk_* descem manualmente uma árvore de tipo para obter a descrição
# estrutural de um tipo.

def walk_tipo_basico(ctx: LA.Tipo_basicoContext) -> Tipo:
    if ctx.getText() == 'literal':
        return Literal()
    elif ctx.getText() == 'inteiro':
        return Inteiro(None)
    elif ctx.getText() == 'real':
        return Real(None)
    elif ctx.getText() == 'logico':
        return Lógico()

def walk_tipo_basico_ident(ts: TS, ctx: LA.Tipo_basico_identContext) -> Tipo:
    if tipo_basico := ctx.tipo_basico():
        return walk_tipo_basico(tipo_basico)
    elif ty := ts.obter_apelido(ctx.IDENT().getText()):
        return ty
    else:
        line = ctx.IDENT().symbol.line
        tstr = ctx.IDENT().getText()
        raise TypeResolutionError(f'Linha {line}: tipo {tstr} nao declarado')

def walk_tipo_estendido(ts: TS, ctx: LA.Tipo_estendidoContext) -> Tipo:
    if ctx.getText()[:1] == '^': # TODO Não sei se essa é a melhor ideia.
        return Ponteiro(walk_tipo_basico_ident(ts, ctx.tipo_basico_ident()))
    else:
        return walk_tipo_basico_ident(ts, ctx.tipo_basico_ident())

def bw_dimensao(ts: TS, ctx: LA.DimensaoContext, tipo: Tipo) -> Tipo:
    for exp_aritmetica in ctx.exp_aritmetica():
        dim = Expr.walk_exp_aritmetica(ts, exp_aritmetica)
        if not isinstance(dim, Inteiro) or not dim.valor:
            raise TypeResolutionError('Dimensão não é um inteiro')
        elif not dim.valor:
            raise TypeResolutionError('Dimensão não é conhecida no tempo de '
                                      'compilação')
        else:
            tipo = Vetor(tipo, dim.valor)
    return tipo

def bw_registro_implicito(ctx: LA.IdentificadorContext, tipo: Tipo) -> Tipo:
    if len(ctx.IDENT()) > 1:
        print(f'INFO: Identificador {ctx.getText()} declara um registro implícito.')
    for key in ctx.IDENT()[:0:-1]:
        tipo = Registro({ key.getText(): tipo })
    return tipo

def bw_identificador(ts: TS, ctx: LA.IdentificadorContext, tipo: Tipo) -> Tipo:
    tipo = bw_registro_implicito(ctx, tipo)
    return bw_dimensao(ts, ctx.dimensao(), tipo)

def walk_variavel(ts: TS, ctx: LA.VariavelContext) -> List[Tuple[str, Tipo]]:
    out = []
    tipo = walk_tipo(ts, ctx.tipo())
    for identificador in ctx.identificador():
        ident = identificador.IDENT()[0].getText()
        out.append((ident, bw_identificador(ts, identificador, tipo)))
    return out

def walk_registro(ts: TS, ctx: LA.RegistroContext):
    campos = {}
    for variavel in ctx.variavel():
        for ident, tipo in walk_variavel(ts, variavel):
            if ident in campos:
                raise Exception("campo de registro repetido")
            else:
                campos[ident] = tipo
    return Registro(campos)

def walk_tipo(ts, ctx):
    if registro := ctx.registro():
        return walk_registro(ts, registro)
    elif tipo_estendido := ctx.tipo_estendido():
        return walk_tipo_estendido(ts, tipo_estendido)
