from LAParser import LAParser
import LASemanticoTipo

# Um erro de tipo na resolução de uma expressão.
class ExpressionTypeError(Exception):
    pass

def is_arith(t):
    return t == LASemanticoTipo.Inteiro or t == LASemanticoTipo.Real

# As funções chk_* verificam a aplicação de uma classe de operações a um tipo.

def chk_arith(ta, op, tb):
    if is_arith(ta) and is_arith(tb):
        return LASemanticoTipo.Real
    elif op.getText() == '+' and ta == tb == LASemanticoTipo.Literal:
        return LASemanticoTipo.Literal
    else:
        raise ExpressionTypeError(ta, op.getText(), tb)

def chk_neg(t):
    if is_arith(t):
        return t
    else:
        raise ExpressionTypeError
    
def chk_rel(ta, op, tb):
    if is_arith(ta) and is_arith(tb):
        return LASemanticoTipo.Lógico
    elif op.getText() in ['=', '<>'] and ta == tb:
        return LASemanticoTipo.Lógico
    else:
        raise ExpressionTypeError

def chk_bool(ta, _, tb):
    if ta == tb == LASemanticoTipo.Lógico:
        return LASemanticoTipo.Lógico
    else:
        raise ExpressionTypeError

def chk_not(t):
    if t == LASemanticoTipo.Lógico:
        return LASemanticoTipo.Lógico
    else:
        raise ExpressionTypeError

def chk_attr(t, name):
    if a := t.campos.get(name):
        return a
    else:
        raise ExpressionTypeError

def chk_index(ta, tb):
    if ta == LASemanticoTipo.Vetor and is_arith(tb):
        return ta.interno
    else:
        raise ExpressionTypeError

def chk_deref():
    pass # TODO

# As funções walk_* descem manualmente em uma expressão para obter o seu tipo.
# Levantando exceções se a expressão possuir um erro de tipo.

def walk_ident(ts, nomeVar):
    return ts.get(nomeVar)

def walk_identificador(ts, ctx: LAParser.IdentificadorContext):
    if ctx.IDENT():
        if len(ctx.IDENT()) > 1:
            raise Exception # TODO Arrumar indexação
        nomeVar = ctx.IDENT()[0].getText()
        if not ts.get(nomeVar):
            line = ctx.IDENT()[0].symbol.line
            msg = f'Linha {line}: identificador {nomeVar} nao declarado'
            raise ExpressionTypeError(msg)
        return walk_ident(ts, nomeVar)
    
        # TODO ARRUMAR INDEXAÇÃO
        return walk_dimensao(ts, ctx.dimensao())

def walk_dimensao(ts, ctx: LAParser.DimensaoContext):
    ret = None
    for exp_aritmetica in ctx.exp_aritmetica():
        aux = walk_exp_aritmetica(ts, exp_aritmetica)
        if ret != None != aux:
            raise ExpressionTypeError
        else:
            ret = aux
    return ret

def walk_parcela_unario(ts, ctx: LAParser.Parcela_unarioContext):
    if identificador := ctx.identificador():
        return walk_identificador(ts, identificador)
    elif ctx.NUM_INT():
        return LASemanticoTipo.Inteiro
    elif ctx.NUM_REAL():
        return LASemanticoTipo.Real
    elif ctx.IDENT():
        # TODO Chamadas não funcionam ainda
        nomeVar = ctx.IDENT().getText()
        if not ts.get(nomeVar):
            raise ExpressionTypeError
        return walk_ident(ts, nomeVar)
    else:
        return walk_expressao(ts, ctx.expressao()[0])

def walk_parcela_nao_unario(ts, ctx: LAParser.Parcela_nao_unarioContext):
    if ctx.CADEIA():
        return LASemanticoTipo.Literal
    else:
        return walk_identificador(ts, ctx.identificador())

def walk_parcela(ts, ctx: LAParser.ParcelaContext):
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

def walk_fator(ts, ctx):
    return dwc(ts, ctx.parcela(), ctx.op3(), walk_parcela, chk_arith)

def walk_termo(ts, ctx):
    return dwc(ts, ctx.fator(), ctx.op2(), walk_fator, chk_arith)

def walk_exp_aritmetica(ts, ctx):
    return dwc(ts, ctx.termo(), ctx.op1(), walk_termo, chk_arith)

def walk_exp_relacional(ts, ctx):
    return dwc(ts, ctx.exp_aritmetica(), [ctx.op_relacional()], walk_exp_aritmetica, chk_rel)

def walk_parcela_logica(ts, ctx):
    if exp_relacional := ctx.exp_relacional():
        return walk_exp_relacional(ts, exp_relacional)
    else:
        return LASemanticoTipo.Lógico

def walk_fator_logico(ts, ctx):
    if ctx.op_logico_0():
        return chk_not(walk_parcela_logica(ts, ctx.parcela_logica()))
    else:
        return walk_parcela_logica(ts, ctx.parcela_logica())

def walk_termo_logico(ts, ctx):
    return dwc(ts, ctx.fator_logico(), ctx.op_logico_2(), walk_fator_logico, chk_bool)

def walk_expressao(ts, ctx):
    return dwc(ts, ctx.termo_logico(), ctx.op_logico_1(), walk_termo_logico, chk_bool)

def dwc(ts, ctx, op, walk, chk):
    ctx = [walk(ts, c) for c in ctx]
    out = ctx[0]
    for i in range(len(ctx) - 1):
        out = chk(out, op[i], ctx[i + 1])
    return out
