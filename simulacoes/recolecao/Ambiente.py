# implementacoes/recolecao.py
import random
from Core.definicoes import Observacao, Acao , ModoOperacao
from Core.Ambiente import Ambiente
from Core.Agente import Agente

class AmbienteRecolecao(Ambiente):
    def __init__(self, largura: int, altura: int, pos_ninho: tuple):
        super().__init__()
        self.largura = largura
        self.altura = altura
        self.ninho = pos_ninho

        # Estruturas específicas da Recoleção
        self.mapa_recursos = {}  # { (x,y): valor_do_recurso }
        self.inventario_agentes = {}  # { agente: quantidade_carregada }
        self.recursos_totais_depositados = 0
        self.capacidade_maxima = 5

    def observacaoPara(self, agente: Agente) -> Observacao:
        pos_atual = self.posicoes_agentes.get(agente, (0, 0))
        x, y = pos_atual

        # 1. Encontrar o recurso mais próximo
        recurso_mais_proximo = None
        menor_distancia = float('inf')
        for pos_recurso in self.mapa_recursos.keys():
            dist = abs(pos_recurso[0] - x) + abs(pos_recurso[1] - y)
            if dist < menor_distancia:
                menor_distancia = dist
                recurso_mais_proximo = pos_recurso

        # 2. NOVO: Radar de Paredes (Limites do mapa ou obstáculos)
        radar = {
            "CIMA": (x, y - 1) in self.obstaculos or (y - 1) < 0,
            "BAIXO": (x, y + 1) in self.obstaculos or (y + 1) >= self.altura,
            "ESQ": (x - 1, y) in self.obstaculos or (x - 1) < 0,
            "DIR": (x + 1, y) in self.obstaculos or (x + 1) >= self.largura,
        }

        dados = {
            "posicao": pos_atual,
            "no_ninho": pos_atual == self.ninho,
            "carga": self.inventario_agentes.get(agente, 0),
            "pos_ninho": self.ninho,
            "pos_recurso_proximo": recurso_mais_proximo,
            "radar_paredes": radar # Enviamos o radar para o agente
        }
        return Observacao(dados=dados)

    def atualizacao(self) -> None:
        # Nasce um recurso novo com 10% de probabilidade em cada turno
        if random.random() < 0.10:
            rx = random.randint(0, self.largura - 1)
            ry = random.randint(0, self.altura - 1)
            pos = (rx, ry)

            # Não faz spawn no ninho nem em cima de obstáculos
            if pos != self.ninho and pos not in self.obstaculos:
                self.mapa_recursos[pos] = random.randint(1, 5) # Recurso vale 1 a 5 pontos

    def agir(self, accao: Acao, agente: Agente) -> float:
        pos_atual = self.posicoes_agentes.get(agente, (0, 0))
        recompensa = -0.1 # Custo de andar

        # 1. Movimento
        movimentos = {"CIMA": (0, -1), "BAIXO": (0, 1), "ESQ": (-1, 0), "DIR": (1, 0)}
        if accao.tipo in movimentos:
            dx, dy = movimentos[accao.tipo]
            nova_pos = (pos_atual[0] + dx, pos_atual[1] + dy)

            # Valida limites e colisões
            if (0 <= nova_pos[0] < self.largura and
                    0 <= nova_pos[1] < self.altura and
                    nova_pos not in self.obstaculos):
                self.posicoes_agentes[agente] = nova_pos
            else:
                recompensa = -5.0 # CASTIGO POR BATER NUMA PAREDE (Acelera a aprendizagem)

        # 2. Apanhar Recurso
        elif accao.tipo == "APANHAR":
            carga_atual = self.inventario_agentes.get(agente, 0)

            # Só consegue apanhar se houver recurso E tiver espaço na mochila
            if pos_atual in self.mapa_recursos and carga_atual < self.capacidade_maxima:
                valor = self.mapa_recursos.pop(pos_atual)
                self.inventario_agentes[agente] = carga_atual + valor # Acumula no inventário!
                recompensa = 20.0
            else:
                recompensa = -1.0 # Castigo se tentar apanhar o ar ou estiver cheio

                # 3. Depositar no Ninho
        elif accao.tipo == "DEPOSITAR":
            carga = self.inventario_agentes.get(agente, 0)
            if pos_atual == self.ninho and carga > 0:
                self.recursos_totais_depositados += carga
                self.inventario_agentes[agente] = 0
                recompensa = 50.0
            else:
                recompensa = -1.0

        return recompensa

    def reset(self):
        """Repõe o ambiente para um novo episódio de aprendizagem."""
        with self._lock:
            self.mapa_recursos = {(2, 2): 5, (18, 18): 3, (5, 15): 2, (15, 5): 4}
            self.inventario_agentes = {}
            self.recursos_totais_depositados = 0

            # Repõe os agentes no ninho
            for agente in self.posicoes_agentes.keys():
                self.posicoes_agentes[agente] = self.ninho

