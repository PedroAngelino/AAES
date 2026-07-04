import random

from Core.Agente import Agente
from Core.definicoes import Observacao, Acao
from Core.Ambiente import Ambiente


class AmbienteFarol(Ambiente):
    def __init__(self, largura: int, altura: int):
        super().__init__()
        self.largura = largura
        self.altura = altura
        self.pos_farol = (largura // 2, altura // 2)
        self.obstaculos = []
        self.reset()
        self.alcancou_farol = False

    def reset(self):
        with self._lock:
            self.alcancou_farol = False
            # 1. Gerar obstáculos aleatórios (ex: 20 obstáculos)
            self.obstaculos = []
            for _ in range(25):
                obs = (random.randint(0, self.largura-1), random.randint(0, self.altura-1))
                if obs != self.pos_farol:
                    self.obstaculos.append(obs)

            # 2. Resetar agentes para posições aleatórias (longe do farol)
            for agente in self.posicoes_agentes.keys():
                self.posicoes_agentes[agente] = (random.randint(0, self.largura-1), random.randint(0, self.altura-1))

    def observacaoPara(self, agente: Agente) -> Observacao:

        if agente not in self.posicoes_agentes:
            self.posicoes_agentes[agente] = (0, 0)

        pos = self.posicoes_agentes[agente]

        # Direção para o farol (quantizada em 8 setores para facilitar a aprendizagem)
        dx = self.pos_farol[0] - pos[0]
        dy = self.pos_farol[1] - pos[1]
        # Calcular setor (0 a 7)
        import math
        ang = (math.atan2(dy, dx) + math.pi) / (2 * math.pi) * 8
        setor = int(ang) % 8

        # Radar de paredes (4 direções)
        radar = {
            "CIMA": (pos[0], pos[1]-1) in self.obstaculos or (pos[1]-1 < 0),
            "BAIXO": (pos[0], pos[1]+1) in self.obstaculos or (pos[1]+1 >= self.altura),
            "ESQ": (pos[0]-1, pos[1]) in self.obstaculos or (pos[0]-1 < 0),
            "DIR": (pos[0]+1, pos[1]) in self.obstaculos or (pos[0]+1 >= self.largura),
        }

        return Observacao(dados={"setor_farol": setor, "radar": radar})

    def objetivo_alcancado(self):
        return self.alcancou_farol

    def atualizacao(self) -> None:
        """Método obrigatório definido na interface base."""
        # No problema do Farol, o ambiente é estático (o farol não se mexe),
        # por isso não precisamos de código aqui, mas o método tem de existir!
        pass

    def agir(self, accao: Acao, agente: Agente) -> float:
        pos = self.posicoes_agentes[agente]
        # Mapa de ações (dx, dy)
        mapa_acoes = {"N": (0, -1), "S": (0, 1), "O": (-1, 0), "E": (1, 0), "NE": (1, -1), "NO": (-1, -1), "SE": (1, 1), "SO": (-1, 1)}

        dx, dy = mapa_acoes.get(accao.tipo, (0, 0))
        nova_pos = (pos[0] + dx, pos[1] + dy)

        if (0 <= nova_pos[0] < self.largura and 0 <= nova_pos[1] < self.altura and nova_pos not in self.obstaculos):
            self.posicoes_agentes[agente] = nova_pos
            if nova_pos == self.pos_farol:
                self.alcancou_farol = True
                return 100.0 # Objetivo atingido!
            return -0.01      # Custo de tempo

        return -10.0 # Bateu na parede!

