from T1.Tipo import *
from T1.LAVisitor import LAVisitor
from T1.LAParser import LAParser as LA
from T1.TabelaDeSimbolos import TabelaDeSimbolos
from T1 import Codegen, Expr, TRes


class LAtrError(Exception):
    pass


class FormattingError(Exception):
    pass


def format_string(t: Tipo) -> str:
    if is_literal(t):
        return '%s'
    elif is_inteiro(t):
        return '%lld'
    elif is_real(t):
        return '%lf'
    elif is_lógico(t):
        return '%d'
    elif is_ponteiro(t):
        return '%p'
    else:
        raise FormattingError(f'tipo {t} não pode ser lido nem escrito')


def chk_atribuicao_escalar(line, lhs, tl, tr):
    if is_vetor(tl) or is_vetor(tr):
        raise LAtrError('impossível atribuir um vetor')
    if is_aritmético(tl) and is_aritmético(tr):
        return
    if is_void(tr):
        raise LAtrError(f'tentou atrubuir tipo void')
    elif tl != tr:
        print(line, tl, tr)
        raise LAtrError(f'Linha {line}: atribuicao nao compativel para {lhs}')


def chk_atribuicao(ts: TabelaDeSimbolos, attr, rhs_tipo):
    lhs = attr.identificador()
    line = lhs.IDENT()[0].symbol.line
    simbolo = lhs.IDENT()[0].getText()
    lhs_tipo = ts.obter_variavel(simbolo)
    lhs_str = lhs.getText()
    if not lhs_tipo:
        raise LAtrError(f'Linha {line}: identificador {simbolo} nao declarado')
    # Resolver indireção
    if attr.getText()[0] == '^': # TODO Não sei se essa é a melhor ideia.
        if not is_ponteiro(lhs_tipo):
            raise LAtrError(f'Linha {line}: tentou indirecionar um não-ponteiro')
        lhs_tipo = lhs_tipo.interno
        lhs_str = '^' + lhs_str
    # Resolver dimensão
    for exp_aritmetica in lhs.dimensao().exp_aritmetica():
        indice_tipo = Expr.walk_exp_aritmetica(ts, exp_aritmetica)
        if not is_inteiro(indice_tipo):
            raise LAtrError(f'Linha {line}: índice da atribuicao não é inteiro')
        if not is_vetor(lhs_tipo):
            raise LAtrError(f'Linha {line}: expressão da atribuição indexada não é vetor')
        lhs_tipo = lhs_tipo.interno
    # Resolver membros
    for ident in lhs.IDENT()[:0:-1]:
        if not is_registro(lhs_tipo):
            raise LAtrError(f'Linha {line}: expressão da atribuição indexada não é registro')
        if not lhs_tipo.campos.get(ident.getText()):
            raise LAtrError(f'Linha {line}: índice {ident} da atribuição indexada não existe')
        lhs_tipo = lhs_tipo.campos[ident.getText()]
    # Resolver tipo escalar
    chk_atribuicao_escalar(line, lhs_str, lhs_tipo, rhs_tipo)


class LASemantico(LAVisitor):
    def __init__(self):
        self.tss = [ TabelaDeSimbolos({}) ]
        self.scope = []
        self.errors = []
        self.output = []
        self.decls = {}

    def visitCorpo(self, ctx: LA.CorpoContext):
        if self.scope == []:
            self.output.append('void main() {')
            out = super().visitCorpo(ctx)
            self.output.append('}')
            return out
        else:
            return super().visitCorpo(ctx)

    def visitDeclaracao_global(self, ctx: LA.Declaracao_globalContext):
        print('declaracao gloral')
        line = ctx.IDENT().symbol.line
        simbolo = ctx.IDENT().getText()
        # Inserir uma variável Void temporariamente na tabela, pois não sabemos
        # o tipo da função/procedimento ainda.
        if self.tss[-1].ocupado(simbolo):
            self.errors.append(f'Linha {line}: identificador {simbolo} ja '
                                'declarado anteriormente')
            return
        else:
            self.tss[-1].inserir_variavel(simbolo, Void())
        # Empilhar uma cópia da tabela para o escopo interno.
        self.tss.append(self.tss[-1].copiar())
        # Descobrir os tipos da entrada da função.
        entrada = []
        args_code = []
        if parametros := ctx.parametros():
            for parametro in parametros.parametro():
                tipo_estendido = parametro.tipo_estendido()
                tipo = TRes.walk_tipo_estendido(self.tss[-1], tipo_estendido)
                for identificador in parametro.identificador():
                    tipo_bw = TRes.bw_identificador(self.tss[-1], identificador, tipo)
                    simbolo = identificador.IDENT()[0].getText()
                    entrada.append(tipo_bw)
                    if not self.tss[-1].ocupado(simbolo):
                        self.tss[-1].inserir_variavel(simbolo, tipo_bw)
                    else:
                        line = identificador.IDENT()[0].symbol.line
                        self.errors.append(f'Linha {line}: identificador {simbolo} '
                                            'ja declarado anteriormente')
                    # Gerar código do parâmetro.
                    args_code.append(f'{Codegen.type_string(self.decls, tipo_bw)} '
                                     f'{Codegen.walk_ident(simbolo)}')
        # Descobrir o tipo da saída e inserir na tabela, substituindo o Void.
        # HACK Copiamos a função para o escopo externo *e* o escopo interno.
        simbolo = ctx.IDENT().getText()
        saida = Void()
        if tipo_estendido := ctx.tipo_estendido():
            saida = TRes.walk_tipo_estendido(self.tss[-1], tipo_estendido)
        self.tss[-2].inserir_variavel(simbolo, Função(entrada, saida))
        self.tss[-1].inserir_variavel(simbolo, Função(entrada, saida))
        self.scope.append(Função(entrada, saida))
        # Gerar código da declaração.
        self.output.append(f'{Codegen.type_string(self.decls, saida)} ')
        self.output.append(f'{Codegen.walk_ident(simbolo)}(')
        self.output.append(','.join(args_code))
        self.output.append('){')
        # Visitar o corpo.
        out = super().visitDeclaracao_global(ctx)
        # Desempilhar a tabela do escopo interno.
        self.tss.pop()
        self.scope.pop()
        # Gerar código do fim do bloco.
        self.output.append('}')
        return out

    def visitDeclaracao_local(self, ctx: LA.Declaracao_localContext):
        if variavel := ctx.variavel():
            # TODO walk_variavel?
            # Resolver o tipo da variável.
            tipo = Void()
            try:
                tipo = TRes.walk_tipo(self.tss[-1], variavel.tipo())
            except TRes.TypeResolutionError as e:
                self.errors.append(str(e))
            # Popular a tabela com os identificadores declarados.
            for identificador in variavel.identificador():
                try:
                    tipo_bw = None
                    # Se o tipo for invalido, colocamos Void na tabela.
                    # Nesse caso, não fazemos o backwalk nas variáveis. pois caso
                    # isso acontecesse, teríamos tipos absurdos como Vetor(Void, 2).
                    if not is_void(Tipo):
                        tipo_bw = TRes.bw_identificador(self.tss[-1], identificador, tipo)
                    simbolo = identificador.IDENT()[0].getText()
                    if not self.tss[-1].ocupado(simbolo):
                        self.tss[-1].inserir_variavel(simbolo, tipo_bw)
                    else:
                        line = identificador.IDENT()[0].symbol.line
                        self.errors.append(f'Linha {line}: identificador '
                                           f'{simbolo} ja declarado '
                                            'anteriormente')
                    # Gerar código da declaração.
                    self.output.append(f'{Codegen.type_string(self.decls, tipo_bw)} ')
                    self.output.append(f'{Codegen.walk_ident(simbolo)};')
                except TRes.TypeResolutionError as e:
                    self.errors.append(str(e))
                except Expr.ExpressionTypeError as e:
                    self.errors.append(str(e))
        elif constante := ctx.valor_constante():
            line = ctx.IDENT().symbol.line
            simbolo = ctx.IDENT().getText()
            tipo_lhs = TRes.walk_tipo_basico(ctx.tipo_basico())
            tipo_rhs = Expr.walk_valor_constante(constante)
            if self.tss[-1].ocupado(simbolo):
                self.errors.append(f'Linha {line}: identificador {simbolo} ja '
                                    'declarado anteriormente')
            try:
                chk_atribuicao_escalar(line, simbolo, tipo_lhs, tipo_rhs)
            except LAtrError as e:
                self.errors.append(str(e))
            self.tss[-1].inserir_variavel(simbolo, tipo_rhs)
            # Gerar código da declaração.
            self.output.append(f'static {Codegen.type_string(self.decls, tipo_lhs)} ')
            self.output.append(f'{Codegen.walk_ident(simbolo)} = ')
            self.output.append(f'{constante.getText()};')
        elif tipo := ctx.tipo():
            line = ctx.IDENT().symbol.line
            simbolo = ctx.IDENT().getText()
            tipo = TRes.walk_tipo(self.tss[-1], tipo)
            if self.tss[-1].ocupado(simbolo):
                self.errors.append(f'Linha {line}: tipo {simbolo} ja  declarado'
                                    ' anteriormente')
            else:
                self.tss[-1].inserir_apelido(simbolo, tipo)
            # Não geramos código aqui.
            # O resolvedor estrutural já resolve apelidos de tipo sozinho.
        return super().visitDeclaracao_local(ctx)

    def visitCmdSe(self, ctx: LA.CmdSeContext):
        try:
            # TODO precisa ser lógico? talvez?
            Expr.walk_expressao(self.tss[-1], ctx.expressao())
        except Expr.ExpressionTypeError as e:
            self.errors.append(str(e))
        # Gerar código do comando.
        self.output.append(f'if({Codegen.walk_expressao(ctx.expressao())}){{')
        out = super().visitCmdSe(ctx)
        self.output.append('}')
        return out

    def visitSenao(self, ctx: LA.SenaoContext):
        self.output.append('} else {')
        return super().visitSenao(ctx)

    def visitItem_selecao(self, ctx: LA.Item_selecaoContext):
        for numero_intervalo in ctx.constantes().numero_intervalo():
            rg = numero_intervalo.NUM_INT()
            if len(rg) == 1:
                self.output.append(f'case {rg[0]}:')
            else:
                self.output.append(f'case {rg[0]} ... {rg[1]}:')
        out = super().visitItem_selecao(ctx)
        self.output.append('break;')
        return out

    def visitCmdCaso(self, ctx: LA.CmdCasoContext):
        if not is_inteiro(Expr.walk_exp_aritmetica(self.tss[-1], ctx.exp_aritmetica())):
            raise TRes.TypeResolutionError('tentou fazer caso com não-inteiro')
        # Gerar código do comando.
        self.output.append(f'switch({Codegen.walk_exp_aritmetica(ctx.exp_aritmetica())}){{')
        out = super().visitCmdCaso(ctx)
        self.output.append('}')
        return out

    def visitPadrao(self, ctx: LA.PadraoContext):
        self.output.append('default:')
        out = super().visitPadrao(ctx)
        self.output.append('break;')
        return out

    def visitCmdPara(self, ctx: LA.CmdParaContext):
        # TODO concatenar a expressão na tabela de simbolos
        for exp_aritmetica in ctx.exp_aritmetica():
            try:
                Expr.walk_exp_aritmetica(self.tss[-1], exp_aritmetica)
            except Expr.ExpressionTypeError as e:
                self.errors.append(str(e))
        # Gerar código do comando.
        simbolo = Codegen.walk_ident(ctx.IDENT().getText())
        el, eh = ctx.exp_aritmetica()
        self.output.append('for(T_inteiro ')
        self.output.append(f'{simbolo} = ')
        self.output.append(f'{Codegen.walk_exp_aritmetica(el)};')
        self.output.append(f'{simbolo} <= {Codegen.walk_exp_aritmetica(eh)};')
        self.output.append(f'{simbolo}++){{')
        out = super().visitCmdPara(ctx)
        self.output.append('}')
        return out

    def visitCmdFaca(self, ctx: LA.CmdFacaContext):
        try:
            Expr.walk_expressao(self.tss[-1], ctx.expressao())
        except Expr.ExpressionTypeError as e:
            self.errors.append(str(e))
        # Gerar código do comando.
        self.output.append('do {')
        out = super().visitCmdFaca(ctx)
        self.output.append(f'}} while ({Codegen.walk_expressao(ctx.expressao())});')
        return out

    def visitCmdAtribuicao(self, ctx: LA.CmdAtribuicaoContext):
        try:
            tipo = Expr.walk_expressao(self.tss[-1], ctx.expressao())
            chk_atribuicao(self.tss[-1], ctx, tipo);
            # Gerar código do comando.
            if is_literal(tipo):
                self.output.append(f'strcpy(')
                self.output.append(f'{Codegen.walk_identificador(ctx.identificador())}, ')
                self.output.append(f'{Codegen.walk_expressao(ctx.expressao())});')
            else:
                if ctx.getText()[0] == '^': # TODO Não sei se essa é a melhor ideia.
                    self.output.append(f'*({Codegen.walk_identificador(ctx.identificador())}) = ')
                else:
                    self.output.append(f'{Codegen.walk_identificador(ctx.identificador())} = ')
                self.output.append(f'{Codegen.walk_expressao(ctx.expressao())};')
        except Expr.ExpressionTypeError:
            line = ctx.identificador().IDENT()[0].symbol.line
            simbolo = ctx.identificador().IDENT()[0].getText()
            self.errors.append(f'Linha {line}: atribuicao nao compativel para '
                               f'{simbolo}')
        except LAtrError as e:
            self.errors.append(str(e))
        return super().visitCmdAtribuicao(ctx)

    def visitCmdEnquanto(self, ctx: LA.CmdEnquantoContext):
        try:
            Expr.walk_expressao(self.tss[-1], ctx.expressao())
        except Expr.ExpressionTypeError as e:
            self.errors.append(str(e))
        # Gerar código do comando.
        self.output.append(f'while ({Codegen.walk_expressao(ctx.expressao())}) {{')
        out = super().visitCmdEnquanto(ctx)
        self.output.append('}')
        return out

    def visitCmdChamada(self, ctx: LA.CmdChamadaContext):
        code_args = []
        for expressao in ctx.expressao():
            try:
                Expr.walk_expressao(self.tss[-1], expressao)
            except Expr.ExpressionTypeError as e:
                self.errors.append(str(e))
            code_args.append(Codegen.walk_expressao(expressao))
        # Gerar código do comando.
        code_args = ','.join(code_args)
        self.output.append(f'{Codegen.walk_ident(ctx.IDENT().getText())}({code_args});')
        return super().visitCmdChamada(ctx)

    def visitCmdRetorne(self, ctx: LA.CmdRetorneContext):
        try:
            tipo = Expr.walk_expressao(self.tss[-1], ctx.expressao())
            if self.scope == []:
                self.errors.append(f'Linha {ctx.start.line}: comando retorne nao permitido nesse escopo')
            elif is_void(self.scope[-1].saída):
                self.errors.append(f'Linha {ctx.start.line}: comando retorne nao permitido nesse escopo')
            elif self.scope[-1].saída != tipo:
                self.errors.append(f'Linha {ctx.start.line}: tipo de retorno invalido')
        except Expr.ExpressionTypeError as e:
            self.errors.append(str(e))
        # Gerar código do comando.
        self.output.append(f'return {Codegen.walk_expressao(ctx.expressao())};')
        return super().visitCmdRetorne(ctx)

    def visitCmdLeia(self, ctx: LA.CmdLeiaContext):
        for identificador in ctx.identificador():
            try:
                tipo = Expr.walk_identificador(self.tss[-1], identificador)
                self.output.append(f'scanf("{format_string(tipo)}", &{Codegen.walk_identificador(identificador)});')
            except Expr.ExpressionTypeError as e:
                self.errors.append(str(e))
        return super().visitCmdLeia(ctx)

    def visitCmdEscreva(self, ctx: LA.CmdEscrevaContext):
        for expressao in ctx.expressao():
            try:
                tipo = Expr.walk_expressao(self.tss[-1], expressao)
                self.output.append(f'printf("{format_string(tipo)}", {Codegen.walk_expressao(expressao)});')
            except Expr.ExpressionTypeError as e:
                self.errors.append(str(e))
        return super().visitCmdEscreva(ctx)

    def outstr(self) -> str:
        return '\n'.join(['#include <stdio.h>', '#include <stdlib.h>'] + list(self.decls.values()) + self.output)
