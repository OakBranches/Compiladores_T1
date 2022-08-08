from dataclasses import dataclass
from typing import Dict
from T1.Tipo import Tipo

class Elemento:
    pass

@dataclass
class Apelido(Elemento):
    tipo: Tipo

@dataclass
class Variavel(Elemento):
    tipo: Tipo

@dataclass
class Constante(Elemento):
    tipo: Tipo

class TabelaDeSimbolos:
    def __init__(self, t: Dict[str, Elemento]):
        self.t = t

    def __repr__(self) -> str:
        out = [ '{' ]
        for k in self.t.keys():
            out.append(f'{k} => {self.t[k]}')
        return '\n\t'.join(out) + '\n}'

    def inserir_apelido(self, simbolo: str, tipo: Tipo):
        self.t[simbolo] = Apelido(tipo)

    def inserir_variavel(self, simbolo: str, tipo: Tipo):
        self.t[simbolo] = Variavel(tipo)

    def inserir_constante(self, simbolo: str, tipo: Tipo):
        self.t[simbolo] = Constante(tipo)

    def ocupado(self, simbolo: str) -> bool:
        return self.t.get(simbolo) != None

    def obter_apelido(self, simbolo: str) -> Tipo:
        if isinstance(self.t.get(simbolo), Apelido):
            return self.t[simbolo].tipo

    def obter_variavel(self, simbolo: str) -> Tipo:
        if isinstance(self.t.get(simbolo), Variavel):
            return self.t[simbolo].tipo

    def obter_constante(self, simbolo: str) -> Tipo:
        if isinstance(self.t.get(simbolo), Constante):
            return self.t[simbolo].tipo

    def copiar(self):
        return TabelaDeSimbolos(self.t.copy())
