lexer grammar LA;

SELF: 'algoritmo'|'declare'|':'|'escreva'|
    'literal'|'inteiro'|'leia'|'('|')'|','|'fim_algoritmo'| 
    '>' | '>=' | '<' | '<=' | '<>' | '='| 'real' |'<-'|
    '+' | '-' | '*' | '/';


CADEIA     : '"' ( ESC_SEQ | ~('"'|'\\') )* '"';
fragment
ESC_SEQ    : '\\"';

COMENTARIO:'{'  ('\\}'|~('}'|'\\'))* '}';

NUM_INT	: ('+'|'-')?('0'..'9')+;

NUM_REAL	: ('+'|'-')?('0'..'9')+ ('.' ('0'..'9')+)?;

IDENT: ([a-z])([a-zA-Z]|[0-9])*;

WS  :   ( ' '
        | '\t'
        | '\r'
        | '\n'
        ) 
    ;