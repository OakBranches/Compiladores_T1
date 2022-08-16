from cmd import Cmd
from T1.Tipo import *
from T1.LAVisitor import LAVisitor
from T1.LAParser import LAParser as LA
from T1.TabelaDeSimbolos import TabelaDeSimbolos
from T1 import Expr, TRes


class LAtrError(Exception):
    pass


def regularized_expression(exp):
    texto = exp.getText()
    texto = texto.replace("=","==").replace(">==",">=")
    texto = texto.replace("<==","<=").replace("<>","!=")
    return texto.replace('nao',"!")

def chk_atribuicao_escalar(line, lhs, tl, tr):
    if is_vetor(tl) or is_vetor(tr):
        raise LAtrError('impossível atribuir um vetor')
    if is_aritmético(tl) and is_aritmético(tr):
        return
    if is_ponteiro(tl) and is_inteiro(tr):
        return
    if is_void(tr):
        raise LAtrError(f'tentou atrubuir tipo void')
    elif tl != tr:
        print(tl, tr)
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
        self.output = ["#include <stdio.h>\n", "#include <stdlib.h>\n"]

    def visitPrograma(self, ctx: LA.ProgramaContext):
        result = self.defaultResult()
        n = ctx.getChildCount()
        for i in range(n):
            if not self.shouldVisitNextChild(ctx, result):
                return result

            c = ctx.getChild(i)
            if str(c) == "algoritmo":
                self.output.append("int main(){\n")
            if str(c) == "fim_algoritmo":
                self.output.append("}\n")
            childResult = c.accept(self)
            result = self.aggregateResult(result, childResult)
            
        return result

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
        parametros_str = ""
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
                        if is_literal(tipo_bw):
                            parametros_str += f"{tipo_bw.c_declar()}* {simbolo},"
                        else:
                            parametros_str += f"{tipo_bw.c_declar()} {simbolo},"


                    else:
                        line = identificador.IDENT()[0].symbol.line
                        self.errors.append(f'Linha {line}: identificador {simbolo} '
                                            'ja declarado anteriormente')
        # Descobrir o tipo da saída e inserir na tabela, substituindo o Void.
        # HACK Copiamos a função para o escopo externo *e* o escopo interno.
        simbolo = ctx.IDENT().getText()
        saida = Void()
        if tipo_estendido := ctx.tipo_estendido():
            saida = TRes.walk_tipo_estendido(self.tss[-1], tipo_estendido)
        
        self.tss[-2].inserir_variavel(simbolo, Função(entrada, saida))
        self.tss[-1].inserir_variavel(simbolo, Função(entrada, saida))
        self.scope.append(Função(entrada, saida))

        self.output.append(f"{saida.c_declar()} {simbolo}({parametros_str[:-1]}){{")

        # Visitar o corpo.
        out = super().visitDeclaracao_global(ctx)

        self.output.append("}")
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
                        if is_literal(tipo_bw):
                            self.output.append(f"{tipo_bw.c_declar()} {simbolo}[80];\n")
                        elif is_vetor(tipo_bw):
                            self.output.append(f"{tipo_bw.c_declar()} {simbolo}[{tipo_bw.tamanho}];\n")
                        elif not is_registro(tipo_bw):
                            self.output.append(f"{tipo_bw.c_declar()} {simbolo};\n")
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
                self.output.append(f"const {tipo_rhs.c_declar()} {simbolo} = {ctx.valor_constante().getText()};\n")
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
            expressao = ctx.expressao() 
            self.output.append(f"if ({regularized_expression(expressao)}){{\n")
            Expr.walk_expressao(self.tss[-1], expressao)
        except Expr.ExpressionTypeError as e:
            self.errors.append(str(e))
        
        walk = self.defaultResult()
        n = ctx.getChildCount()
        for i in range(n):
            if not self.shouldVisitNextChild(ctx, walk):
                break
            c = ctx.getChild(i)
            if str(c) == 'senao':
                self.output.append("}else{\n")
            childResult = c.accept(self)
            walk = self.aggregateResult(walk, childResult)

        self.output.append("}\n")
        return walk
    
    def visitCmdPara(self, ctx: LA.CmdParaContext):
        # TODO concatenar a expressão na tabela de simbolos
        exps = ctx.exp_aritmetica()
        for exp_aritmetica in exps:
            try:
                Expr.walk_exp_aritmetica(self.tss[-1], exp_aritmetica)
            except Expr.ExpressionTypeError as e:
                self.errors.append(str(e))
        res = f"for({ctx.IDENT()} = {exps[0].getText()};"
        res += f"{ctx.IDENT()} <= {exps[1].getText()};"
        res += f"{ctx.IDENT()}++){{"
        self.output.append(res)
        walk = super().visitCmdPara(ctx)
        self.output.append("}")
        return walk

    def visitCmdFaca(self, ctx: LA.CmdFacaContext):
        try:
            Expr.walk_expressao(self.tss[-1], ctx.expressao())
        except Expr.ExpressionTypeError as e:
            self.errors.append(str(e))
        self.output.append("do{")
        walk = super().visitCmdFaca(ctx)
        self.output.append(f"}}while({regularized_expression(ctx.expressao())});")
        return walk

    def visitCmdAtribuicao(self, ctx: LA.CmdAtribuicaoContext):
        try:
            espressao = ctx.expressao()
            tipo = Expr.walk_expressao(self.tss[-1], espressao)
            chk_atribuicao(self.tss[-1], ctx, tipo)
            str_id = ctx.identificador().getText()
            if ctx.getText()[0] == "^":
                str_id = "*" + str_id
            if is_literal(tipo):
                self.output.append(f"strcpy({str_id},{espressao.getText()});")
            else:
                self.output.append(f"{str_id} = {espressao.getText()};")
        except Expr.ExpressionTypeError:
            line = ctx.identificador().IDENT()[0].symbol.line
            simbolo = ctx.identificador().IDENT()[0].getText()
            self.errors.append(f'Linha {line}: atribuicao nao compativel para '
                               f'{simbolo}')
        except LAtrError as e:
            self.errors.append(str(e))
        return super().visitCmdAtribuicao(ctx)

    def visitCmdEnquanto(self, ctx: LA.CmdEnquantoContext):
        exp = ctx.expressao()
        try:
            Expr.walk_expressao(self.tss[-1], exp)
        except Expr.ExpressionTypeError as e:
            self.errors.append(str(e))
        self.output.append(f"while({regularized_expression(exp)}){{")
        walk = super().visitCmdEnquanto(ctx)
        self.output.append("}")
        return walk

    def visitCmdChamada(self, ctx: LA.CmdChamadaContext):
        for expressao in ctx.expressao():
            try:
                Expr.walk_expressao(self.tss[-1], expressao)
            except Expr.ExpressionTypeError as e:
                self.errors.append(str(e))

        p = ""
        for i in ctx.expressao():
            p += regularized_expression(i) + ';'

        self.output.append(f"{ctx.IDENT()}({p[:-1]});")

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
            else:
                self.output.append(f"return {regularized_expression(ctx.expressao())};")
        except Expr.ExpressionTypeError as e:
            self.errors.append(str(e))
        return super().visitCmdRetorne(ctx)

    def visitCmdLeia(self, ctx: LA.CmdLeiaContext):
        for identificador in ctx.identificador():
            try:
                out = Expr.walk_identificador(self.tss[-1], identificador)
                if is_inteiro(out):
                    scanType = "d" 
                elif is_literal(out):
                    scanType = "s"
                else: 
                    scanType = "f" 
                
                self.output.append(f"scanf(\"%{scanType}\",&{identificador.getText()});")
            except Expr.ExpressionTypeError as e:
                self.errors.append(str(e))
        return super().visitCmdLeia(ctx)

    def visitCmdEscreva(self, ctx: LA.CmdEscrevaContext):
        for expressao in ctx.expressao():
            try:
                out = Expr.walk_expressao(self.tss[-1], expressao)
                print_type = None
                if is_inteiro(out):
                    print_type = "d"
                elif is_real(out):
                    print_type = "f"
                elif is_literal(out):
                    print_type = "s"
                if print_type:
                    self.output.append(f"printf(\"%{print_type}\",{expressao.getText()});")
                else:
                    self.output.append(f"printf({expressao.getText()});")

            except Expr.ExpressionTypeError as e:
                self.errors.append(str(e))
        return super().visitCmdEscreva(ctx)

    def visitCmdCaso(self, ctx: LA.CmdCasoContext):
        self.output.append(f"switch ({ctx.exp_aritmetica().getText()}){{\n")
        walk = self.defaultResult()

        n = ctx.getChildCount()
        for i in range(n):
            if not self.shouldVisitNextChild(ctx, walk):
                break

            c = ctx.getChild(i)
            if str(c) == "senao":
                self.output.append("default:")

            childResult = c.accept(self)
            walk = self.aggregateResult(walk, childResult)

        self.output.append("}")
        return walk

    def visitItem_selecao(self, ctx: LA.Item_selecaoContext):
        for j in ctx.constantes().numero_intervalo():
            if len(j.NUM_INT()) > 1:
                a, b = map(int, j.getText().split(".."))
                for i in range(a,b+1):
                    self.output.append(f"case {i}:\n")
            else:
                self.output.append(f"case {j.getText()}:\n")
        walk = super().visitItem_selecao(ctx)
        self.output.append(f"break;\n")
        return walk
     
    def visitRegistro(self, ctx: LA.RegistroContext):
        self.output.append("struct{")
        walk = super().visitRegistro(ctx)
        for v in ctx.variavel():
            tipo: Tipo = TRes.walk_tipo(self.tss[-1], v.tipo())
            for i in v.identificador():
                if is_literal(tipo):
                    self.output.append(f"{tipo.c_declar()} {i.getText()}[80];")
                else:
                    self.output.append(f"{tipo.c_declar()} {i.getText()};")
        # TODO
        self.output.append("}reg;")
        return walk