from enum import Enum

class Observacao:
    """Representa o estado do ambiente percecionado pelo agente."""
    def __init__(self, dados=None):
        self.dados = dados

class Acao:
    """Representa uma ação escolhida e executada pelo agente."""
    def __init__(self, tipo=None):
        self.tipo = tipo

class Sensor:
    """Representa um sensor que pode ser acoplado a um agente."""
    def __init__(self, nome=None):
        self.nome = nome

class ModoOperacao(Enum):
    APRENDIZAGEM = "1"
    TESTE = "2"
    ALEATORIO = "3"


