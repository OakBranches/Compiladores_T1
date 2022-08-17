grammar LA;

// Ignorado
COMENTARIO: '{' ('\\}' | ~('}' | '{' | '\\' | '\n'))* '}' -> skip;
WS: (' ' | '\t' | '\r' | '\n') -> skip;

// Identificadores
IDENT: ([a-zA-Z]) ([a-zA-Z] | [0-9] | '_')*;
variavel: identificador (',' identificador)* ':' tipo;
identificador: IDENT ('.' IDENT)* dimensao;
dimensao: ('[' exp_aritmetica ']')*;

// Literais
// Chamados aqui de "valores constantes".
CADEIA: '"' ( ESC_SEQ | ~('"' | '\\' | '\n') )* '"';
fragment ESC_SEQ: '\\"' | '\\n';
NUM_INT: /*('+' | '-')?*/ ('0'..'9')+;
NUM_REAL: /*('+' | '-')?*/ ('0'..'9')+ ('.' ('0'..'9')+)?;
valor_constante: CADEIA | NUM_INT | NUM_REAL | 'verdadeiro' | 'falso';

// Tipos
tipo_basico: 'literal' | 'inteiro' | 'real' | 'logico';
tipo_basico_ident: tipo_basico | IDENT;
tipo_estendido: '^'? tipo_basico_ident;
registro: 'registro' variavel* 'fim_registro';
tipo: registro | tipo_estendido;

// Expressões
op1: '+' | '-';
op2: '*' | '/';
op3: '%';
op_unario: '-';
op_relacional: '=' | '<>' | '>=' | '<=' | '>' | '<';
op_logico_0: 'nao';
op_logico_1: 'ou';
op_logico_2: 'e';
parcela_unario: '^'? identificador
    | IDENT '(' expressao (',' expressao)* ')'
    | NUM_INT
    | NUM_REAL
    | '(' expressao ')';
parcela_nao_unario: '&' identificador | CADEIA;
parcela: op_unario? parcela_unario | parcela_nao_unario;
fator: parcela (op3 parcela)*;
termo: fator (op2 fator)*;
exp_aritmetica: termo (op1 termo)*;
exp_relacional: exp_aritmetica (op_relacional exp_aritmetica)?;
parcela_logica: 'verdadeiro' | 'falso' | exp_relacional;
fator_logico: op_logico_0? parcela_logica;
termo_logico: fator_logico (op_logico_2 fator_logico)*;
expressao: termo_logico (op_logico_1 termo_logico)*;

// Comando 'caso'
numero_intervalo: op_unario? NUM_INT ( '..' op_unario? NUM_INT)?;
constantes: numero_intervalo (',' numero_intervalo)*;
item_selecao: constantes ':' cmd*;
selecao: item_selecao*;
padrao: 'senao' cmd*;
cmdCaso: 'caso' exp_aritmetica 'seja' selecao padrao? 'fim_caso';

// Comandos
senao: 'senao' cmd*;
cmdSe: 'se' expressao 'entao' cmd* senao? 'fim_se';
cmdPara: 'para' IDENT '<-' exp_aritmetica 'ate' exp_aritmetica 'faca' cmd* 'fim_para';
cmdEnquanto: 'enquanto' expressao 'faca' cmd* 'fim_enquanto';
cmdFaca: 'faca' cmd* 'ate' expressao;
cmdAtribuicao: '^'? identificador '<-' expressao;
cmdChamada: IDENT '(' expressao (',' expressao)* ')';
cmdRetorne: 'retorne' expressao;
// Nota: "leia" e "escreva" parecem chamadas de função, mas são unidades
// sintáticas. PHP também comete esse erro.
cmdLeia: 'leia' '(' '^'? identificador (',' '^'? identificador)* ')';
cmdEscreva: 'escreva' '(' expressao (',' expressao)* ')';
cmd: cmdLeia
    | cmdEscreva
    | cmdSe
    | cmdCaso
    | cmdPara
    | cmdEnquanto
    | cmdFaca
    | cmdAtribuicao
    | cmdChamada
    | cmdRetorne;

// Funções e procedimentos
parametro: 'var'? identificador (',' identificador)* ':' tipo_estendido;
parametros: parametro (',' parametro)*;
declaracao_local: 'declare' variavel
    | 'constante' IDENT ':' tipo_basico '=' valor_constante
    | 'tipo' IDENT ':' tipo;
corpo: declaracao_local* cmd*;
declaracao_global:
      'procedimento' IDENT '(' parametros? ')' corpo 'fim_procedimento'
    | 'funcao' IDENT '(' parametros? ')' ':' tipo_estendido corpo 'fim_funcao';

// Top level
declaracoes: (declaracao_local | declaracao_global)*;
programa: declaracoes 'algoritmo' corpo 'fim_algoritmo';
