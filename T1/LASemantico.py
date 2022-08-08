from T1.Tipo import *
from T1.LAListener import LAListener
from T1.TabelaDeSimbolos import TabelaDeSimbolos
from T1 import Expr, TRes


class LAtrError(Exception):
    pass


def chk_atribuicao_escalar(line, simbolo, tl, tr):
    if isinstance(tl, Vetor) or isinstance(tr, Vetor):
        raise LAtrError('impossível atribuir um vetor')
    if isinstance(tl, Aritmético) and isinstance(tr, Aritmético):
        return
    if isinstance(tr, Void):
        raise LAtrError(f'tentou atrubuir tipo void')
    elif tl != tr:
        raise LAtrError(f'Linha {line}: atribuicao nao compativel para {simbolo}')


def chk_atribuicao(ts: TabelaDeSimbolos, lhs, rhs_tipo):
    line = lhs.IDENT()[0].symbol.line
    simbolo = lhs.IDENT()[0].getText()
    lhs_tipo = ts.obter_variavel(simbolo)
    if not lhs_tipo:
        raise LAtrError(f'Linha {line}: identificador {simbolo} nao declarado')
    # Resolver dimensão
    for exp_aritmetica in lhs.dimensao().exp_aritmetica():
        indice_tipo = Expr.walk_exp_aritmetica(ts, exp_aritmetica)
        if not isinstance(indice_tipo, Inteiro):
            raise LAtrError(f'Linha {line}: índice da atribuicao não é inteiro')
        if not isinstance(lhs_tipo, Vetor):
            raise LAtrError(f'Linha {line}: expressão da atribuição indexada não é vetor')
        lhs_tipo = lhs_tipo.interno
    # Resolver membros
    for ident in lhs.IDENT()[:0:-1]:
        if not isinstance(lhs_tipo, Registro):
            raise LAtrError(f'Linha {line}: expressão da atribuição indexada não é registro')
        if not lhs_tipo.campos.get(ident.getText()):
            raise LAtrError(f'Linha {line}: índice {ident} da atribuição indexada não existe')
        lhs_tipo = lhs_tipo.campos[ident.getText()]
    # Resolver tipo escalar
    chk_atribuicao_escalar(line, simbolo, lhs_tipo, rhs_tipo)


class LASemantico(LAListener):
    def __init__(self):
        self.tss = [ TabelaDeSimbolos({}) ]
        self.errors = []

    def enterDeclaracao_global(self, ctx):
        self.tss.append(self.tss[-1].copiar())
        return super().enterDeclaracoes(ctx)

    def exitDeclaracao_global(self, ctx):
        self.tss.pop()
        return super().exitDeclaracao_global(ctx)

    def exitDeclaracao_local(self, ctx):
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
                tipo_bw = None
                # Se o tipo for invalido, colocamos Void na tabela.
                # Nesse caso, não fazemos o backwalk nas variáveis. pois caso
                # isso acontecesse, teríamos tipos absurdos como Vetor(Void, 2).
                if not isinstance(Tipo, Void):
                    tipo_bw = TRes.bw_identificador(self.tss[-1], identificador, tipo)
                simbolo = identificador.IDENT()[0].getText()
                if not self.tss[-1].ocupado(simbolo):
                    self.tss[-1].inserir_variavel(simbolo, tipo_bw)
                else:
                    line = identificador.IDENT()[0].symbol.line
                    self.errors.append(f'Linha {line}: identificador {simbolo} '
                                        'ja declarado anteriormente')
        elif constante := ctx.valor_constante():
            line = ctx.IDENT().symbol.line
            simbolo = ctx.IDENT().getText()
            tipo_lhs = TRes.walk_tipo_basico_ident(self.tss[-1], ctx.tipo_basico())
            tipo_rhs = Expr.walk_valor_constante(constante)
            if self.tss[-1].ocupado(simbolo):
                self.errors.append(f'Linha {line}: identificador {simbolo} ja '
                                    'declarado anteriormente')
            try:
                chk_atribuicao_escalar(line, simbolo, tipo_lhs, tipo_rhs)
            except LAtrError as e:
                self.errors.append(str(e))
        elif tipo := ctx.tipo():
            line = ctx.IDENT().symbol.line
            simbolo = ctx.IDENT().getText()
            tipo = TRes.walk_tipo(self.tss[-1], tipo)
            if self.tss[-1].ocupado(simbolo):
                self.errors.append(f'Linha {line}: tipo {simbolo} ja  declarado'
                                    ' anteriormente')
            else:
                self.tss[-1].inserir_apelido(simbolo, tipo)
        return super().exitDeclaracao_local(ctx)

    def exitCmdSe(self, ctx):
        try:
            Expr.walk_expressao(self.tss[-1], ctx.expressao())
        except Expr.ExpressionTypeError as e:
            self.errors.append(str(e))
        return super().exitCmdSe(ctx)

    def exitCmdPara(self, ctx):
        for exp_aritmetica in ctx.exp_aritmetica():
            try:
                Expr.walk_exp_aritmetica(self.tss[-1], exp_aritmetica)
            except Expr.ExpressionTypeError as e:
                self.errors.append(str(e))
        return super().exitCmdPara(ctx)

    def exitCmdFaca(self, ctx):
        try:
            Expr.walk_expressao(self.tss[-1], ctx.expressao())
        except Expr.ExpressionTypeError as e:
            self.errors.append(str(e))
        return super().exitCmdFaca(ctx)

    def exitCmdAtribuicao(self, ctx):
        try:
            tipo = Expr.walk_expressao(self.tss[-1], ctx.expressao())
            chk_atribuicao(self.tss[-1], ctx.identificador(), tipo);
        except Expr.ExpressionTypeError:
            line = ctx.identificador().IDENT()[0].symbol.line
            simbolo = ctx.identificador().IDENT()[0].getText()
            self.errors.append(f'Linha {line}: atribuicao nao compativel para '
                               f'{simbolo}')
        except LAtrError as e:
            self.errors.append(str(e))
        return super().exitCmdAtribuicao(ctx)

    def exitCmdEnquanto(self, ctx):
        try:
            Expr.walk_expressao(self.tss[-1], ctx.expressao())
        except Expr.ExpressionTypeError as e:
            self.errors.append(str(e))
        return super().exitCmdEnquanto(ctx)

    def exitCmdChamada(self, ctx):
        for expressao in ctx.expressao():
            try:
                Expr.walk_expressao(self.tss[-1], expressao)
            except Expr.ExpressionTypeError as e:
                self.errors.append(str(e))
        return super().exitCmdChamada(ctx)

    def exitCmdRetorne(self, ctx):
        try:
            Expr.walk_expressao(self.tss[-1], ctx.expressao())
        except Expr.ExpressionTypeError as e:
            self.errors.append(str(e))
        return super().exitCmdRetorne(ctx)

    def exitCmdLeia(self, ctx):
        for identificador in ctx.identificador():
            try:
                Expr.walk_identificador(self.tss[-1], identificador)
            except Expr.ExpressionTypeError as e:
                self.errors.append(str(e))
        return super().exitCmdLeia(ctx)

    def exitCmdEscreva(self, ctx):
        for expressao in ctx.expressao():
            try:
                Expr.walk_expressao(self.tss[-1], expressao)
            except Expr.ExpressionTypeError as e:
                self.errors.append(str(e))
        return super().exitCmdEscreva(ctx)
