lexer grammar LA;

SELF: 'algoritmo'|'declare'|':'|'escreva'|'literal'|'inteiro'|'leia'|'('|')'|','|'fim_algoritmo';


CADEIA     : '"' ( ESC_SEQ | ~('"'|'\\') )* '"';
fragment
ESC_SEQ    : '\\"';

COMENTARIO:'{'  ('\\}'|~('}'|'\\'))* '}';

IDENT: [a-z]+;
WS  :   ( ' '
        | '\t'
        | '\r'
        | '\n'
        ) 
    ;
OP_REL	:	'>' | '>=' | '<' | '<=' | '<>' | '='
	;
OP_ARIT	:	'+' | '-' | '*' | '/'
	;
