lexer grammar LA;

SELF: 'algoritmo'|'declare'|':'|'escreva'|
    'literal'|'inteiro'|'leia'|'('|')'|','|'fim_algoritmo'| 
    '>' | '>=' | '<' | '<=' | '<>' | '='| 'real' |'<-'|
    '+' | '-' | '*' | '/' | 'e' | 'nao' | 'logico' | 'ou' | 
    'entao' | 'senao' | 'fim_se' | 'fim_caso' | 'para' | 'ate' |
    'faca' | 'fim_para' | 'retorne' | 'funcao' | 'fim_funcao' | '[' | ']' |
    'procedimento' | 'var' | 'fim_procedimento' | 'verdadeiro' | 'se'| '..' |
    'caso' | 'seja' | 'enquanto' | 'fim_enquanto' | '%' | '^' | '&' | 'registro' |
    'fim_registro' | '.' | 'tipo' | 'constante' | 'falso';

CADEIA: '"' ( ESC_SEQ | ~('"'|'\\') )* '"';
fragment ESC_SEQ: '\\"';

COMENTARIO: '{' ('\\}' | ~('}' | '\\'))* '}';

NUM_INT: /*('+' | '-')?*/ ('0'..'9')+;

NUM_REAL: /*('+' | '-')?*/ ('0'..'9')+ ('.' ('0'..'9')+)?;

IDENT: ([a-zA-Z]) ([a-zA-Z] | [0-9]| '_')*;

WS: (' ' | '\t' | '\r' | '\n');
