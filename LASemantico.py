from LAListener import LAListener
import LASemanticoExpr, LASemanticoTipo


def ok_attr(a, b):
    if LASemanticoExpr.is_arith(a) and LASemanticoExpr.is_arith(b):
        return True
    else:
        return a == b


class LASemantico(LAListener):
    def __init__(self):
        # TODO As tabelas não deveriam ser separadas.
        self.itss = [ {} ] # Tabela de símbolos (identificador → tipo)
        self.ttss = [ {} ] # Tabela de símbolos (tipo → tipo)
        self.errors = []

    def enterDeclaracao_global(self, ctx):
        self.itss.append(self.itss[-1].copy())
        self.ttss.append(self.ttss[-1].copy())
        return super().enterDeclaracoes(ctx)

    def exitDeclaracao_global(self, ctx):
        self.itss.pop()
        self.ttss.pop()
        return super().exitDeclaracao_global(ctx)

    def exitDeclaracao_local(self, ctx):
        if variavel := ctx.variavel():
            # Resolver o tipo da variável.
            tipo = LASemanticoTipo.Void
            try:
                tipo = LASemanticoTipo.walk_tipo(self.ttss[-1], variavel.tipo())
            except LASemanticoTipo.TypeResolutionError as e:
                self.errors.append(str(e))
            # Popular a tabela com os identificadores declarados.
            for identificador in variavel.identificador():
                if len(identificador.IDENT()) > 1:
                    raise Exception("eu não sei o que fazer nesse caso")
                simbolo = identificador.IDENT()[0].getText()
                if simbolo in self.itss[-1]:
                    line = identificador.IDENT()[0].symbol.line
                    self.errors.append(f'Linha {line}: identificador {simbolo} '
                                        'ja declarado anteriormente')
                else:
                    self.itss[-1][simbolo] = tipo
        else:
            # TODO Outras declarações locais
            pass
        return super().exitDeclaracao_local(ctx)

    # Os métodos abaixo são aproximadamente a mesma coisa: Identificar
    # expressões para verificar com o walk_expressao.

    def exitCmdSe(self, ctx):
        try:
            LASemanticoExpr.walk_expressao(self.itss[-1], ctx.expressao())
        except LASemanticoExpr.ExpressionTypeError as e:
            self.errors.append(str(e))
        return super().exitCmdSe(ctx)

    def exitCmdPara(self, ctx):
        for exp_aritmetica in ctx.exp_aritmetica():
            try:
                LASemanticoExpr.walk_exp_aritmetica(self.itss[-1], exp_aritmetica)
            except LASemanticoExpr.ExpressionTypeError as e:
                self.errors.append(str(e))
        return super().exitCmdPara(ctx)

    def exitCmdFaca(self, ctx):
        try:
            LASemanticoExpr.walk_expressao(self.itss[-1], ctx.expressao())
        except LASemanticoExpr.ExpressionTypeError as e:
            self.errors.append(str(e))
        return super().exitCmdFaca(ctx)

    def exitCmdAtribuicao(self, ctx):
        line = ctx.identificador().IDENT()[0].symbol.line
        simbolo = ctx.identificador().IDENT()[0].getText()
        try:
            tipo = LASemanticoExpr.walk_expressao(self.itss[-1], ctx.expressao())
            if not self.itss[-1].get(simbolo):
                self.errors.append(f'Linha {line}: identificador {simbolo} '
                                    'nao declarado')
            if not ok_attr(tipo, self.itss[-1].get(simbolo)):
                self.errors.append(f'Linha {line}: atribuicao nao compativel '
                                   f'para {simbolo}')
        except LASemanticoExpr.ExpressionTypeError:
            self.errors.append(f'Linha {line}: atribuicao nao compativel para '
                               f'{simbolo}')
        return super().exitCmdAtribuicao(ctx)

    def exitCmdEnquanto(self, ctx):
        try:
            LASemanticoExpr.walk_expressao(self.itss[-1], ctx.expressao())
        except LASemanticoExpr.ExpressionTypeError as e:
            self.errors.append(str(e))
        return super().exitCmdEnquanto(ctx)

    def exitCmdChamada(self, ctx):
        for expressao in ctx.expressao():
            try:
                LASemanticoExpr.walk_expressao(self.itss[-1], expressao)
            except LASemanticoExpr.ExpressionTypeError as e:
                self.errors.append(str(e))
        return super().exitCmdChamada(ctx)

    def exitCmdRetorne(self, ctx):
        try:
            LASemanticoExpr.walk_expressao(self.itss[-1], ctx.expressao())
        except LASemanticoExpr.ExpressionTypeError as e:
            self.errors.append(str(e))
        return super().exitCmdRetorne(ctx)

    def exitCmdLeia(self, ctx):
        for identificador in ctx.identificador():
            try:
                LASemanticoExpr.walk_identificador(self.itss[-1], identificador)
            except LASemanticoExpr.ExpressionTypeError as e:
                self.errors.append(str(e))
        return super().exitCmdLeia(ctx)

    def exitCmdEscreva(self, ctx):
        for expressao in ctx.expressao():
            try:
                LASemanticoExpr.walk_expressao(self.itss[-1], expressao)
            except LASemanticoExpr.ExpressionTypeError as e:
                self.errors.append(str(e))
        return super().exitCmdEscreva(ctx)
