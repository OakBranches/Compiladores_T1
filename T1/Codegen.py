from T1.Tipo import *
from T1.LAParser import LAParser as LA

# Transforma um tipo em uma string, manipulando um conjunto de declarações de
# tipo no processo. Esta é a alma da tipagem estrutural.
def type_string(decls, ty: Tipo) -> str:
    out = None
    if is_literal(ty):
        out = 'T_literal'
        decls[out] = 'typedef char T_literal[80];'
    elif is_inteiro(ty):
        out = 'T_inteiro'
        decls[out] = 'typedef long long int T_inteiro;'
    elif is_real(ty):
        out = 'T_real'
        decls[out] = 'typedef double T_real;'
    elif is_lógico(ty):
        out = 'T_logico'
        decls[out] = 'typedef int T_logico;'
    elif is_ponteiro(ty):
        interno_str = type_string(decls, ty.interno)
        out = f'T_ponteiro_{len(interno_str)}_{interno_str}'
        decls[out] = f'typedef {interno_str} * {out};'
    elif is_vetor(ty):
        interno_str = type_string(decls, ty.interno)
        out = f'T_vetor_{ty.tamanho}_{len(interno_str)}_{interno_str}'
        decls[out] = f'typedef {interno_str} {out}[{ty.tamanho}];'
    elif is_registro(ty):
        out = 'T_registro'
        chaves = sorted(ty.campos.keys())
        indecl = ''
        for chave in chaves:
            saida_str = type_string(decls, ty.campos[chave])
            out += f'_{len(chave)}_{chave}_{len(saida_str)}_{saida_str}'
            indecl += f'{saida_str} {chave};'
        decls[out] = f'typedef struct {out} {{{indecl}}} {out};'
    elif is_função(ty):
        out = 'T_func'
        indecl = []
        for entrada in ty.entrada:
            entrada_str = type_string(decls, entrada)
            out += f'_{len(entrada_str)}_{entrada_str}'
            indecl.append(entrada_str)
        indecl = ','.join(indecl)
        saida_str = type_string(decls, ty.saída)
        out += f'_{len(saida_str)}_{saida_str}'
        decls[out] = f'typedef {saida_str} (*{out})({indecl});'
    elif is_void(ty):
        out = 'T_void'
        decls[out] = 'typedef void T_void;'
    return out

# As funções chk_* traduzem os operadores. :<

def chk_arith(sa: str, op, sb: str) -> str:
    return sa + op.getText() + sb

def chk_rel(sa: str, op, sb: str) -> str:
    if op.getText() == '=':
        return sa + '==' + sb
    elif op.getText() == '<>':
        return sa + '!=' + sb
    else:
        return sa + op.getText() + sb

def chk_bool(sa: str, op, sb: str) -> str:
    if op.getText() == 'e':
        return sa + '&&' + sb
    elif op.getText() == 'ou':
        return sa + '||' + sb

# As funções walk_* descem manualmente em uma expressão para gerar código.

def walk_ident(ident: str) -> str:
    return f'I_{ident}'

def walk_identificador(ctx: LA.IdentificadorContext) -> str:
    if ctx.IDENT():
        out = walk_ident(ctx.IDENT()[0].getText())
        # Resolver campos
        for ident in ctx.IDENT()[1:]:
            out = f'{out}.{ident.getText()}'
        # Resolver índices
        for exp_aritmetica in ctx.dimensao().exp_aritmetica():
            out = f'{out}[{walk_exp_aritmetica(exp_aritmetica)}]'
        return out

def walk_valor_constante(ctx: LA.Valor_constanteContext) -> str:
    if ctx.CADEIA():
        return ctx.getText()
    elif ctx.NUM_INT():
        return ctx.getText()
    elif ctx.NUM_REAL():
        return ctx.getText()
    elif ctx.getText() == 'verdadeiro':
        return '1'
    else:
        return '0'

def walk_parcela_unario(ctx: LA.Parcela_unarioContext) -> str:
    if identificador := ctx.identificador():
        if ctx.getText()[0] == '^': # TODO Não sei se essa é a melhor ideia.
            return f'*{walk_identificador(identificador)}'
        else:
            return walk_identificador(identificador)
    elif ctx.NUM_INT():
        return ctx.NUM_INT().getText()
    elif ctx.NUM_REAL():
        return ctx.NUM_REAL().getText()
    elif ctx.IDENT():
        entrada = []
        for expressao in ctx.expressao():
            entrada.append(walk_expressao(expressao))
        args = ','.join(entrada)
        return f'{walk_ident(ctx.IDENT().getText())}({args})'
    else:
        return f'({walk_expressao(ctx.expressao()[0])})'

def walk_parcela_nao_unario(ctx: LA.Parcela_nao_unarioContext) -> str:
    if ctx.CADEIA():
        return ctx.getText()
    elif ctx.getText()[0] == '&': # TODO Não sei se essa é a melhor ideia.
        return f'&{walk_ident(ctx.getText()[1:])}'
    else:
        return walk_identificador(ctx.identificador())

def walk_parcela(ctx: LA.ParcelaContext) -> str:
    if ctx.op_unario():
        if parcela_nao_unario := ctx.parcela_nao_unario():
            return f'-{walk_parcela_nao_unario(parcela_nao_unario)}'
        elif parcela_unario := ctx.parcela_unario():
            return f'-{walk_parcela_unario(parcela_unario)}'
    else:
        if parcela_nao_unario := ctx.parcela_nao_unario():
            return walk_parcela_nao_unario(parcela_nao_unario)
        elif parcela_unario := ctx.parcela_unario():
            return walk_parcela_unario(parcela_unario)

def walk_fator(ctx: LA.FatorContext) -> str:
    return dwc(ctx.parcela(), ctx.op3(), walk_parcela, chk_arith)

def walk_termo(ctx: LA.TermoContext) -> str:
    return dwc(ctx.fator(), ctx.op2(), walk_fator, chk_arith)

def walk_exp_aritmetica(ctx: LA.Exp_aritmeticaContext) -> str:
    return dwc(ctx.termo(), ctx.op1(), walk_termo, chk_arith)

def walk_exp_relacional(ctx: LA.Exp_relacionalContext) -> str:
    return dwc(ctx.exp_aritmetica(), [ctx.op_relacional()], walk_exp_aritmetica, chk_rel)

def walk_parcela_logica(ctx: LA.Parcela_logicaContext) -> str:
    if exp_relacional := ctx.exp_relacional():
        return walk_exp_relacional(exp_relacional)
    elif ctx.getText() == 'verdadeiro':
        return '1'
    else:
        return '0'

def walk_fator_logico(ctx: LA.Fator_logicoContext) -> str:
    if ctx.op_logico_0():
        return f'!{walk_parcela_logica(ctx.parcela_logica())}'
    else:
        return walk_parcela_logica(ctx.parcela_logica())

def walk_termo_logico(ctx: LA.Termo_logicoContext) -> str:
    return dwc(ctx.fator_logico(), ctx.op_logico_2(), walk_fator_logico, chk_bool)

def walk_expressao(ctx: LA.ExpressaoContext) -> str:
    return dwc(ctx.termo_logico(), ctx.op_logico_1(), walk_termo_logico, chk_bool)

def dwc(ctx, op, walk, chk):
    ctx = [walk(c) for c in ctx]
    out = ctx[0]
    for i in range(len(ctx) - 1):
        out = chk(out, op[i], ctx[i + 1])
    return out
