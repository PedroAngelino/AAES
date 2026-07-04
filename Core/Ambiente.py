# ambiente.py
import threading
from abc import ABC, abstractmethod
from typing import Dict, List, Any

from .definicoes import *
from .Agente import Agente

class Ambiente(ABC):

    def __init__(self):
        """
        Inicializa as estruturas base do ambiente.
        O Lock garante que as ações concorrentes dos agentes (Threads) não corrompem o estado.
        """
        self._lock = threading.Lock()

        # Estruturas de dados comuns que qualquer ambiente costuma ter
        self.posicoes_agentes: Dict[Agente, Any] = {} # Mapeia o Agente à sua posição (ex: (x, y) ou 'Nodo A')
        self.recursos: List[Any] = []                 # Lista de recursos/comida a recolher
        self.obstaculos: List[Any] = []               # Lista de obstáculos estáticos ou dinâmicos

    @abstractmethod
    def observacaoPara(self, agente: Agente) -> Observacao:
        """
        Devolve uma perspetiva do mundo a partir do ponto de vista do agente.
        (ex: O que está nas 8 células em redor do agente numa grelha 2D).
        """
        pass

    @abstractmethod
    def atualizacao(self) -> None:
        """Atualiza a dinâmica global do ambiente (ex: movimento de obstáculos ou spawn de recursos)."""
        pass

    @abstractmethod
    def agir(self, acao: Acao, agente: 'Agente') -> float:
        """
        Aplica a ação, altera o estado e devolve a recompensa do passo.
        """
        pass