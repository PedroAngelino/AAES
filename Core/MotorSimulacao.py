import time
import json
from abc import ABC
from typing import List, Dict, Any
from .Agente import Agente
from .Ambiente import Ambiente

class MotorDeSimulacao(ABC):
    def __init__(self):
        # Variáveis exigidas
        self._agentes: List[Agente] = []
        self._ambiente: Ambiente = None
        self._passos_maximos: int = 200
        self._passo_atual: int = 0
        self._simulacao_terminada: bool = False

        # Variáveis auxiliares para suportar visualização e gráficos
        self.visualizador = None
        self.delay: float = 0.05
        self.historico: List[Dict[str, Any]] = []

    @classmethod
    def cria(cls, nome_do_ficheiro_parametros: str) -> 'MotorDeSimulacao':
        """Inicializador obrigatório pela arquitetura base."""
        motor = cls()
        try:
            with open(nome_do_ficheiro_parametros, 'r') as f:
                config = json.load(f)
                motor._passos_maximos = config.get("passos_maximos", 200)
                print(f"[Motor] Configuração de {nome_do_ficheiro_parametros} carregada.")
        except FileNotFoundError:
            print("[Motor] Aviso: Ficheiro não encontrado. A usar predefinições.")
        return motor

    def listaAgentes(self) -> List[Agente]:
        """Método obrigatório pela arquitetura base."""
        return self._agentes

    def executa(self) -> None:
        """O ciclo principal obrigatório. Gere 1 único episódio/teste."""
        self._passo_atual = 0
        self._simulacao_terminada = False

        while self._passo_atual < self._passos_maximos and not self._simulacao_terminada:
            if self._ambiente:
                self._ambiente.atualizacao()

            for agente in self._agentes:
                agente.executar(self._ambiente)

            # Se houver visualizador acoplado, renderiza
            if self.visualizador:
                self.visualizador.renderizar()
                time.sleep(self.delay)

            self._passo_atual += 1

            # Condição de terminação prematura (Farol)
            if hasattr(self._ambiente, 'objetivo_alcancado') and self._ambiente.objetivo_alcancado():
                self._simulacao_terminada = True

    def executa_episodios(self, numero_episodios: int) -> None:
        """Gere o ciclo de treino, invocando o executa() múltiplas vezes."""
        self.historico = []

        for ep in range(1, numero_episodios + 1):
            if hasattr(self._ambiente, 'reset'):
                self._ambiente.reset()

            self.executa() # Invoca o método obrigatório!

            # Fecho de episódio (para baixar o epsilon, etc.)
            for agente in self._agentes:
                if hasattr(agente, 'fim_episodio'):
                    agente.fim_episodio()

            # Recolha de métricas consoante o ambiente
            if hasattr(self._ambiente, 'recursos_totais_depositados'):
                pontuacao = self._ambiente.recursos_totais_depositados
            else:
                pontuacao = self._passo_atual if self._simulacao_terminada else self._passos_maximos

            self.historico.append({"episodio": ep, "resultado": pontuacao})

            if ep % 100 == 0:
                print(f"Episódio {ep} concluído | Score: {pontuacao}")