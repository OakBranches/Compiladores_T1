from T1.Tipo import *
from math import fmod
from T1.LAParser import LAParser as LA
from T1.TabelaDeSimbolos import TabelaDeSimbolos as TS


# Um erro de tipo na resolução de uma expressão.
class ExpressionTypeError(Exception):
    pass


# As funções chk_* verificam a aplicação de uma classe de operações a um tipo.

def chk_arith(ta: Tipo, op: str, tb: Tipo) -> Tipo:
    if op.getText() == '+':
        if isinstance(ta, Inteiro) and isinstance(tb, Inteiro):
            if ta.valor and tb.valor:
                return Inteiro(ta.valor + tb.valor)
            else:
                return Inteiro(None)
        elif isinstance(ta, Aritmético) and isinstance(tb, Aritmético):
            if ta.valor and tb.valor:
                return Real(ta.valor + tb.valor)
            else:
                return Real(None)
        elif isinstance(ta, Literal) and isinstance(tb, Literal):
            return Literal()
        else:
            raise ExpressionTypeError
    elif op.getText() == '-':
        if isinstance(ta, Inteiro) and isinstance(tb, Inteiro):
            if ta.valor and tb.valor:
                return Inteiro(ta.valor - tb.valor)
            else:
                return Inteiro(None)
        elif isinstance(ta, Aritmético) and isinstance(tb, Aritmético):
            if ta.valor and tb.valor:
                return Real(ta.valor - tb.valor)
            else:
                return Real(None)
        else:
            raise ExpressionTypeError
    elif op.getText() == '*':
        if isinstance(ta, Inteiro) and isinstance(tb, Inteiro):
            if ta.valor and tb.valor:
                return Inteiro(ta.valor * tb.valor)
            else:
                return Inteiro(None)
        elif isinstance(ta, Aritmético) and isinstance(tb, Aritmético):
            if ta.valor and tb.valor:
                return Real(ta.valor * tb.valor)
            else:
                return Real(None)
        else:
            raise ExpressionTypeError
    elif op.getText() == '/':
        if isinstance(ta, Aritmético) and isinstance(tb, Aritmético):
            if ta.valor and tb.valor:
                return Real(ta.valor / tb.valor)
            else:
                return Real(None)
        else:
            raise ExpressionTypeError
    elif op.getText() == '%':
        if isinstance(ta, Inteiro) and isinstance(tb, Inteiro):
            if ta.valor and tb.valor:
                return Inteiro(ta.valor % tb.valor)
            else:
                return Inteiro(None)
        elif isinstance(ta, Aritmético) and isinstance(tb, Aritmético):
            if ta.valor and tb.valor:
                return Real(fmod(ta.valor, tb.valor))
            else:
                return Real(None)
        else:
            raise ExpressionTypeError

def chk_neg(t: Tipo) -> Tipo:
    if isinstance(t, Aritmético):
        if t.valor:
            return type(t)(-t.valor)
        else:
            return t
    else:
        raise ExpressionTypeError

def chk_rel(ta: Tipo, op: str, tb: Tipo) -> Tipo:
    if isinstance(ta, Aritmético) and isinstance(tb, Aritmético):
        return Lógico()
    elif op.getText() in ['=', '<>'] and ta == tb:
        return Lógico()
    else:
        raise ExpressionTypeError

def chk_bool(ta: Tipo, _, tb: Tipo) -> Tipo:
    if isinstance(ta, Lógico) and isinstance(tb, Lógico):
        return Lógico()
    else:
        raise ExpressionTypeError

def chk_not(t: Tipo) -> Tipo:
    if isinstance(t, Lógico):
        return Lógico()
    else:
        raise ExpressionTypeError

def chk_attr(t: Tipo, name: str) -> Tipo:
    if isinstance(t, Registro) and t.campos.get(name):
        return t.campos[name]
    else:
        raise ExpressionTypeError

def chk_index(ta: Tipo, tb: Tipo) -> Tipo:
    if isinstance(ta, Vetor) and isinstance(tb, Aritmético):
        return ta.interno
    else:
        raise ExpressionTypeError

def chk_call(f: Tipo, t: Tipo) -> Tipo:
    if isinstance(f, Função) and f.entrada == t:
        if isinstance(f.saída, Void):
            raise ExpressionTypeError
        else:
            return f.saída
    else:
        raise ExpressionTypeError

def chk_deref():
    pass # TODO

# As funções walk_* descem manualmente em uma expressão para obter o seu tipo.
# Levantando exceções se a expressão possuir um erro de tipo.

def walk_ident(ts: TS, nomeVar: str) -> Tipo:
    return ts.obter_variavel(nomeVar)

def walk_identificador(ts: TS, ctx: LA.IdentificadorContext) -> Tipo:
    if ctx.IDENT():
        line = ctx.IDENT()[0].symbol.line
        nomeVar = ctx.IDENT()[0].getText()
        if not ts.obter_variavel(nomeVar):
            msg = f'Linha {line}: identificador {nomeVar} nao declarado'
            raise ExpressionTypeError(msg)
        # Tipo do identificador
        out = walk_ident(ts, nomeVar)
        # Resolver campos
        for ident in ctx.IDENT()[1:]:
            if not isinstance(out, Registro):
                raise ExpressionTypeError(f'Linha {line}: tentou indexar um não-registro')
            if out.campos.get(ident.getText()):
                out = out.campos[ident.getText()]
            else:
                raise ExpressionTypeError(f'Linha {line}: tentou indexar um campo que não existe')
        # Resolver índices
        for exp_aritmetica in ctx.dimensao().exp_aritmetica():
            indice = walk_exp_aritmetica(ts, exp_aritmetica)
            if not isinstance(indice, Inteiro):
                raise ExpressionTypeError(f'Linha {line}: tentou indexar com um não-inteiro')
            if not isinstance(out, Vetor):
                raise ExpressionTypeError(f'Linha {line}: tentou indexar um não-vetor')
            out = out.interno
        return out

def walk_valor_constante(ctx: LA.Valor_constanteContext) -> Tipo:
    if ctx.CADEIA():
        return Literal()
    elif ctx.NUM_INT():
        return Inteiro(int(ctx.NUM_INT().getText()))
    elif ctx.NUM_REAL():
        return Real(float(ctx.NUM_REAL().getText()))
    else:
        return Lógico

def walk_parcela_unario(ts: TS, ctx: LA.Parcela_unarioContext) -> Tipo:
    if identificador := ctx.identificador():
        return walk_identificador(ts, identificador)
    elif ctx.NUM_INT():
        return Inteiro(int(ctx.NUM_INT().getText()))
    elif ctx.NUM_REAL():
        return Real(float(ctx.NUM_REAL().getText()))
    elif ctx.IDENT():
        # TODO Chamadas não funcionam ainda
        nomeVar = ctx.IDENT().getText()
        if not ts.obter_variavel(nomeVar):
            raise ExpressionTypeError
        return walk_ident(ts, nomeVar)
    else:
        return walk_expressao(ts, ctx.expressao()[0])

def walk_parcela_nao_unario(ts: TS, ctx: LA.Parcela_nao_unarioContext) -> Tipo:
    if ctx.CADEIA():
        return Literal()
    else:
        return walk_identificador(ts, ctx.identificador())

def walk_parcela(ts: TS, ctx: LA.ParcelaContext) -> Tipo:
    if ctx.op_unario():
        if parcela_nao_unario := ctx.parcela_nao_unario():
            return chk_neg(walk_parcela_nao_unario(ts, parcela_nao_unario))
        elif parcela_unario := ctx.parcela_unario():
            return chk_neg(walk_parcela_unario(ts, parcela_unario))
    else:
        if parcela_nao_unario := ctx.parcela_nao_unario():
            return walk_parcela_nao_unario(ts, parcela_nao_unario)
        elif parcela_unario := ctx.parcela_unario():
            return walk_parcela_unario(ts, parcela_unario)

def walk_fator(ts: TS, ctx: LA.FatorContext) -> Tipo:
    return dwc(ts, ctx.parcela(), ctx.op3(), walk_parcela, chk_arith)

def walk_termo(ts: TS, ctx: LA.TermoContext) -> Tipo:
    return dwc(ts, ctx.fator(), ctx.op2(), walk_fator, chk_arith)

def walk_exp_aritmetica(ts: TS, ctx: LA.Exp_aritmeticaContext) -> Tipo:
    return dwc(ts, ctx.termo(), ctx.op1(), walk_termo, chk_arith)

def walk_exp_relacional(ts: TS, ctx: LA.Exp_relacionalContext) -> Tipo:
    return dwc(ts, ctx.exp_aritmetica(), [ctx.op_relacional()], walk_exp_aritmetica, chk_rel)

def walk_parcela_logica(ts: TS, ctx: LA.Parcela_logicaContext) -> Tipo:
    if exp_relacional := ctx.exp_relacional():
        return walk_exp_relacional(ts, exp_relacional)
    else:
        return Lógico()

def walk_fator_logico(ts: TS, ctx: LA.Fator_logicoContext) -> Tipo:
    if ctx.op_logico_0():
        return chk_not(walk_parcela_logica(ts, ctx.parcela_logica()))
    else:
        return walk_parcela_logica(ts, ctx.parcela_logica())

def walk_termo_logico(ts: TS, ctx: LA.Termo_logicoContext) -> Tipo:
    return dwc(ts, ctx.fator_logico(), ctx.op_logico_2(), walk_fator_logico, chk_bool)

def walk_expressao(ts: TS, ctx: LA.ExpressaoContext) -> Tipo:
    return dwc(ts, ctx.termo_logico(), ctx.op_logico_1(), walk_termo_logico, chk_bool)

def dwc(ts: TS, ctx, op, walk, chk):
    ctx = [walk(ts, c) for c in ctx]
    out = ctx[0]
    for i in range(len(ctx) - 1):
        out = chk(out, op[i], ctx[i + 1])
    return out
