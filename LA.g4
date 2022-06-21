lexer grammar LA;

// Palavras-chave
PALAVRA_CHAVE: 'algoritmo' | 'declare' | ':' | 'escreva' | 'literal' | 'inteiro'
    | 'leia' | '(' | ')' | ',' | 'fim_algoritmo' | '>' | '>=' | '<' | '<='
    | '<>' | '='| 'real' |'<-'| '+' | '-' | '*' | '/' | 'e' | 'nao' | 'logico'
    | 'ou' | 'entao' | 'senao' | 'fim_se' | 'fim_caso' | 'para' | 'ate' | 'faca'
    | 'fim_para' | 'retorne' | 'funcao' | 'fim_funcao' | '[' | ']'
    | 'procedimento' | 'var' | 'fim_procedimento' | 'verdadeiro' | 'se'| '..'
    | 'caso' | 'seja' | 'enquanto' | 'fim_enquanto' | '%' | '^' | '&'
    | 'registro' | 'fim_registro' | '.' | 'tipo' | 'constante' | 'falso';

// Cadeia
CADEIA: '"' ( ESC_SEQ | ~('"' | '\\' | '\n') )* '"';
fragment ESC_SEQ: '\\"';

// Comentário
COMENTARIO: '{' ('\\}' | ~('}' | '{' | '\\' | '\n'))* '}' -> skip;

// Número inteiro
NUM_INT: /*('+' | '-')?*/ ('0'..'9')+;

// Número "real"
NUM_REAL: /*('+' | '-')?*/ ('0'..'9')+ ('.' ('0'..'9')+)?;

// Identificador
IDENT: ([a-zA-Z]) ([a-zA-Z] | [0-9]| '_')*;

// Whitespace
WS: (' ' | '\t' | '\r' | '\n') -> skip;
