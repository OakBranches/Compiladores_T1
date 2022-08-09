from T1.Tipo import *
from T1.LAVisitor import LAVisitor
from T1.LAParser import LAParser as LA
from T1.TabelaDeSimbolos import TabelaDeSimbolos
from T1 import Expr, TRes


class LAtrError(Exception):
    pass


def chk_atribuicao_escalar(line, lhs, tl, tr):
    if is_vetor(tl) or is_vetor(tr):
        raise LAtrError('impossível atribuir um vetor')
    if is_aritmético(tl) and is_aritmético(tr):
        return
    if is_void(tr):
        raise LAtrError(f'tentou atrubuir tipo void')
    elif tl != tr:
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
        lhs_tipo = Ponteiro(lhs_tipo)
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
        # Descobrir o tipo da saída e inserir na tabela, substituindo o Void.
        # HACK Copiamos a função para o escopo externo *e* o escopo interno.
        simbolo = ctx.IDENT().getText()
        if tipo_estendido := ctx.tipo_estendido():
            # Função
            saida = TRes.walk_tipo_estendido(self.tss[-1], tipo_estendido)
            self.tss[-2].inserir_variavel(simbolo, Função(entrada, saida))
            self.tss[-1].inserir_variavel(simbolo, Função(entrada, saida))
            self.scope.append(Função(entrada, saida))
        else:
            # Procedimento
            self.tss[-2].inserir_variavel(simbolo, Função(entrada, Void()))
            self.tss[-1].inserir_variavel(simbolo, Função(entrada, Void()))
            self.scope.append(Função(entrada, Void()))
        # Visitar o corpo.
        out = super().visitDeclaracao_global(ctx)
        # Desempilhar a tabela do escopo interno.
        self.tss.pop()
        self.scope.pop()
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
        elif tipo := ctx.tipo():
            line = ctx.IDENT().symbol.line
            simbolo = ctx.IDENT().getText()
            tipo = TRes.walk_tipo(self.tss[-1], tipo)
            if self.tss[-1].ocupado(simbolo):
                self.errors.append(f'Linha {line}: tipo {simbolo} ja  declarado'
                                    ' anteriormente')
            else:
                self.tss[-1].inserir_apelido(simbolo, tipo)
        return super().visitDeclaracao_local(ctx)

    def visitCmdSe(self, ctx: LA.CmdSeContext):
        try:
            # TODO precisa ser lógico? talvez?
            Expr.walk_expressao(self.tss[-1], ctx.expressao())
        except Expr.ExpressionTypeError as e:
            self.errors.append(str(e))
        return super().visitCmdSe(ctx)

    def visitCmdPara(self, ctx: LA.CmdParaContext):
        # TODO concatenar a expressão na tabela de simbolos
        for exp_aritmetica in ctx.exp_aritmetica():
            try:
                Expr.walk_exp_aritmetica(self.tss[-1], exp_aritmetica)
            except Expr.ExpressionTypeError as e:
                self.errors.append(str(e))
        return super().visitCmdPara(ctx)

    def visitCmdFaca(self, ctx: LA.CmdFacaContext):
        try:
            Expr.walk_expressao(self.tss[-1], ctx.expressao())
        except Expr.ExpressionTypeError as e:
            self.errors.append(str(e))
        return super().visitCmdFaca(ctx)

    def visitCmdAtribuicao(self, ctx: LA.CmdAtribuicaoContext):
        try:
            tipo = Expr.walk_expressao(self.tss[-1], ctx.expressao())
            chk_atribuicao(self.tss[-1], ctx, tipo);
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
        return super().visitCmdEnquanto(ctx)

    def visitCmdChamada(self, ctx: LA.CmdChamadaContext):
        for expressao in ctx.expressao():
            try:
                Expr.walk_expressao(self.tss[-1], expressao)
            except Expr.ExpressionTypeError as e:
                self.errors.append(str(e))
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
        return super().visitCmdRetorne(ctx)

    def visitCmdLeia(self, ctx: LA.CmdLeiaContext):
        for identificador in ctx.identificador():
            try:
                Expr.walk_identificador(self.tss[-1], identificador)
            except Expr.ExpressionTypeError as e:
                self.errors.append(str(e))
        return super().visitCmdLeia(ctx)

    def visitCmdEscreva(self, ctx: LA.CmdEscrevaContext):
        for expressao in ctx.expressao():
            try:
                Expr.walk_expressao(self.tss[-1], expressao)
            except Expr.ExpressionTypeError as e:
                self.errors.append(str(e))
        return super().visitCmdEscreva(ctx)
