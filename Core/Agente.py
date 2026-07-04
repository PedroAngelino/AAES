import threading
from abc import ABC, abstractmethod
import queue
import json
from typing import List, Optional
from .definicoes import *

class Agente(threading.Thread, ABC):

    def __init__(self, id_agente: str):
        super().__init__()
        self.id_agente = id_agente

        # Estruturas comuns a todos os agentes
        self._sensores: List[Sensor] = []
        self._ultima_observacao: Optional[Observacao] = None

        # Caixa de mensagens Thread-Safe (FIFO - First In, First Out)
        self._caixa_mensagens: queue.Queue = queue.Queue()

        # Flag para controlo da Thread
        self._ativo = True

    @classmethod
    @abstractmethod
    def cria(cls, nome_do_ficheiro_parametros: str) -> 'Agente':
        """Inicializa e retorna o Agente com base num ficheiro de parâmetros."""
        pass

    def executar(self, ambiente: 'Ambiente') -> None:
        """
        Orquestra o turno do agente, comunicando diretamente com o ambiente.
        Cumpre os passos 5 a 7 do diagrama de sequência.
        """
        # 5.1 e 5.2 (A -> B e B -> A): Solicitar e receber estado local
        obs = ambiente.observacaoPara(self)
        self.observacao(obs)  # Guarda internamente (método obrigatório do enunciado)

        # 6 (A -> A): Deliberar e selecionar ação
        accao = self.age()

        # 7.1 e 7.2 (A -> B e B -> A): Executar ação e receber recompensa
        if accao is not None:
            recompensa = ambiente.agir(accao, self)

            # Atualiza o estado da aprendizagem (método obrigatório do enunciado)
            self.avaliacaoEstadoAtual(recompensa)

    def instala(self, sensor: Sensor) -> None:
        """Acopla um novo sensor ao agente."""
        self._sensores.append(sensor)
        print(f"[Agente {self.id_agente}] Sensor {sensor.nome} instalado.")

    def comunica(self, mensagem: str, de_agente: 'Agente') -> None:
        """
        Recebe uma mensagem de outro agente e guarda-a na queue.
        Como queue.Queue é Thread-Safe, não precisamos de locks manuais aqui.
        """
        self._caixa_mensagens.put((de_agente, mensagem))

    def run(self):
        """
        Ciclo de vida independente da Thread do Agente.
        Caso o Motor use um modelo totalmente assíncrono, o agente pode ficar à escuta aqui.
        """
        while self._ativo:
            # Se a simulação for ditada pelo Motor (Turnos), esta thread pode
            # simplesmente ficar a aguardar eventos (ex: threading.Event)
            # ou podes gerir tudo pelo Motor e ignorar o run().
            pass