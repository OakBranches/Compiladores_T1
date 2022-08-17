# Generated from LA.g4 by ANTLR 4.10.1
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .LAParser import LAParser
else:
    from LAParser import LAParser

# This class defines a complete generic visitor for a parse tree produced by LAParser.

class LAVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by LAParser#variavel.
    def visitVariavel(self, ctx:LAParser.VariavelContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LAParser#identificador.
    def visitIdentificador(self, ctx:LAParser.IdentificadorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LAParser#dimensao.
    def visitDimensao(self, ctx:LAParser.DimensaoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LAParser#valor_constante.
    def visitValor_constante(self, ctx:LAParser.Valor_constanteContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LAParser#tipo_basico.
    def visitTipo_basico(self, ctx:LAParser.Tipo_basicoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LAParser#tipo_basico_ident.
    def visitTipo_basico_ident(self, ctx:LAParser.Tipo_basico_identContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LAParser#tipo_estendido.
    def visitTipo_estendido(self, ctx:LAParser.Tipo_estendidoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LAParser#registro.
    def visitRegistro(self, ctx:LAParser.RegistroContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LAParser#tipo.
    def visitTipo(self, ctx:LAParser.TipoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LAParser#op1.
    def visitOp1(self, ctx:LAParser.Op1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LAParser#op2.
    def visitOp2(self, ctx:LAParser.Op2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LAParser#op3.
    def visitOp3(self, ctx:LAParser.Op3Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LAParser#op_unario.
    def visitOp_unario(self, ctx:LAParser.Op_unarioContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LAParser#op_relacional.
    def visitOp_relacional(self, ctx:LAParser.Op_relacionalContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LAParser#op_logico_0.
    def visitOp_logico_0(self, ctx:LAParser.Op_logico_0Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LAParser#op_logico_1.
    def visitOp_logico_1(self, ctx:LAParser.Op_logico_1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LAParser#op_logico_2.
    def visitOp_logico_2(self, ctx:LAParser.Op_logico_2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LAParser#parcela_unario.
    def visitParcela_unario(self, ctx:LAParser.Parcela_unarioContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LAParser#parcela_nao_unario.
    def visitParcela_nao_unario(self, ctx:LAParser.Parcela_nao_unarioContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LAParser#parcela.
    def visitParcela(self, ctx:LAParser.ParcelaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LAParser#fator.
    def visitFator(self, ctx:LAParser.FatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LAParser#termo.
    def visitTermo(self, ctx:LAParser.TermoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LAParser#exp_aritmetica.
    def visitExp_aritmetica(self, ctx:LAParser.Exp_aritmeticaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LAParser#exp_relacional.
    def visitExp_relacional(self, ctx:LAParser.Exp_relacionalContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LAParser#parcela_logica.
    def visitParcela_logica(self, ctx:LAParser.Parcela_logicaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LAParser#fator_logico.
    def visitFator_logico(self, ctx:LAParser.Fator_logicoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LAParser#termo_logico.
    def visitTermo_logico(self, ctx:LAParser.Termo_logicoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LAParser#expressao.
    def visitExpressao(self, ctx:LAParser.ExpressaoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LAParser#numero_intervalo.
    def visitNumero_intervalo(self, ctx:LAParser.Numero_intervaloContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LAParser#constantes.
    def visitConstantes(self, ctx:LAParser.ConstantesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LAParser#item_selecao.
    def visitItem_selecao(self, ctx:LAParser.Item_selecaoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LAParser#selecao.
    def visitSelecao(self, ctx:LAParser.SelecaoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LAParser#padrao.
    def visitPadrao(self, ctx:LAParser.PadraoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LAParser#cmdCaso.
    def visitCmdCaso(self, ctx:LAParser.CmdCasoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LAParser#senao.
    def visitSenao(self, ctx:LAParser.SenaoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LAParser#cmdSe.
    def visitCmdSe(self, ctx:LAParser.CmdSeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LAParser#cmdPara.
    def visitCmdPara(self, ctx:LAParser.CmdParaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LAParser#cmdEnquanto.
    def visitCmdEnquanto(self, ctx:LAParser.CmdEnquantoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LAParser#cmdFaca.
    def visitCmdFaca(self, ctx:LAParser.CmdFacaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LAParser#cmdAtribuicao.
    def visitCmdAtribuicao(self, ctx:LAParser.CmdAtribuicaoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LAParser#cmdChamada.
    def visitCmdChamada(self, ctx:LAParser.CmdChamadaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LAParser#cmdRetorne.
    def visitCmdRetorne(self, ctx:LAParser.CmdRetorneContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LAParser#cmdLeia.
    def visitCmdLeia(self, ctx:LAParser.CmdLeiaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LAParser#cmdEscreva.
    def visitCmdEscreva(self, ctx:LAParser.CmdEscrevaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LAParser#cmd.
    def visitCmd(self, ctx:LAParser.CmdContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LAParser#parametro.
    def visitParametro(self, ctx:LAParser.ParametroContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LAParser#parametros.
    def visitParametros(self, ctx:LAParser.ParametrosContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LAParser#declaracao_local.
    def visitDeclaracao_local(self, ctx:LAParser.Declaracao_localContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LAParser#corpo.
    def visitCorpo(self, ctx:LAParser.CorpoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LAParser#declaracao_global.
    def visitDeclaracao_global(self, ctx:LAParser.Declaracao_globalContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LAParser#declaracoes.
    def visitDeclaracoes(self, ctx:LAParser.DeclaracoesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LAParser#programa.
    def visitPrograma(self, ctx:LAParser.ProgramaContext):
        return self.visitChildren(ctx)



del LAParser