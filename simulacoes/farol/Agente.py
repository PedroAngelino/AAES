import random, os, pickle
from Core.Agente import Agente
from Core.definicoes import ModoOperacao, Observacao, Acao


class AgenteFarol(Agente):
    def __init__(self, id_agente: str, modo: ModoOperacao):
        super().__init__(id_agente)
        self.modo = modo
        self.q_table = {}
        self.ficheiro_modelo = "modelo_farol.pkl"
        self.estado_anterior = None
        self.acao_anterior = None
        self.epsilon = 0.1 if modo == ModoOperacao.APRENDIZAGEM else 0.0

    @classmethod
    def cria(cls, nome_do_ficheiro_parametros: str) -> 'Agente':
        return cls(id_agente="Navio_1")

    def _traduzir_estado(self, obs):
        r = obs["radar"]
        radar_str = f"{int(r['CIMA'])}{int(r['BAIXO'])}{int(r['ESQ'])}{int(r['DIR'])}"
        return f"{obs['setor_farol']}_{radar_str}"

    def executar(self, ambiente):

        acoes = ["N", "S", "O", "E", "NE", "NO", "SE", "SO"]

        if self.modo == ModoOperacao.ALEATORIO:
            ambiente.agir(Acao(tipo=random.choice(acoes)), self)
            return

        obs = ambiente.observacaoPara(self)
        estado = self._traduzir_estado(obs.dados)


        if estado not in self.q_table: self.q_table[estado] = {a: 0.0 for a in acoes}

        # Decisão
        if self.modo == ModoOperacao.APRENDIZAGEM and random.random() < self.epsilon:
            escolha = random.choice(acoes)
        else:
            escolha = max(self.q_table[estado], key=self.q_table[estado].get)

        # Agir
        recompensa = ambiente.agir(Acao(tipo=escolha), self)

        # Aprender
        if self.modo == ModoOperacao.APRENDIZAGEM and self.estado_anterior:
            s, a, r = self.estado_anterior, self.acao_anterior, recompensa
            self.q_table[s][a] += 0.1 * (r + 0.9 * max(self.q_table[estado].values()) - self.q_table[s][a])

        self.estado_anterior, self.acao_anterior = estado, escolha

    def observacao(self, obs: Observacao) -> None:
        # Guarda a direção que viu
        self.angulo_farol = obs.dados["direcao_farol"]

    def avaliacaoEstadoAtual(self, recompensa: float) -> None:
        if recompensa == 100.0:
            print(f"[{self.id_agente}] Cheguei ao Farol!")

    def save(self):
        with open(self.ficheiro_modelo, 'wb') as f:
            pickle.dump(self.q_table, f)
        # print(f"Modelo {self.ficheiro_modelo} guardado.") # Opcional

    def load(self):
        if os.path.exists(self.ficheiro_modelo):
            with open(self.ficheiro_modelo, 'rb') as f:
                self.q_table = pickle.load(f)
            # print(f"Modelo {self.ficheiro_modelo} carregado com sucesso!")
        else:
            print(f"Aviso: Não encontrei o ficheiro {self.ficheiro_modelo}. A usar Q-Table vazia.")
