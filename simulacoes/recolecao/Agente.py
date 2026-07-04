import random, os, pickle
from Core.Agente import Agente
from Core.Ambiente import Ambiente
from Core.definicoes import ModoOperacao, Observacao, Acao

class AgenteRecolecao(Agente):
    def __init__(self, id_agente: str, modo: ModoOperacao = ModoOperacao.APRENDIZAGEM):
        super().__init__(id_agente)
        self.modo = modo

        # Parâmetros de Aprendizagem
        self.alpha = 0.1      # Taxa de aprendizagem (o quão rápido muda de ideias)
        self.gamma = 0.95      # Fator de desconto (importância das recompensas futuras)
        self.epsilon = 1.0    # Exploração inicial (100% aleatório no início)
        self.epsilon_min = 0.1
        self.epsilon_decay = 0.99

        # Memória
        self.q_table = {}
        self.ficheiro_modelo = "modelo_recolecao.pkl"
        self.estado_anterior = None
        self.acao_anterior = None
        self.recompensa_anterior = 0.0

    @classmethod
    def cria(cls, nome_do_ficheiro_parametros: str) -> 'Agente':
        return cls(id_agente="Formiga_Inteligente")

    def _traduzir_estado(self, obs_dados: dict) -> str:
        pos_x, pos_y = obs_dados["posicao"]
        tem_carga = obs_dados["carga"] > 0

        carga_atual = obs_dados["carga"]
        quer_regressar = carga_atual >= 5

        # Lê o radar de paredes e converte para um formato simples (ex: "1001" significa parede em Cima e à Direita)
        radar = obs_dados["radar_paredes"]
        paredes = f"{int(radar['CIMA'])}{int(radar['BAIXO'])}{int(radar['ESQ'])}{int(radar['DIR'])}"

        ultima_acao = self.acao_anterior if self.acao_anterior else "NENHUMA"

        if quer_regressar:
            # 1. MODO REGRESSO (Mochila cheia)
            ninho_x, ninho_y = obs_dados["pos_ninho"]
            dir_nx = 0 if pos_x == ninho_x else (1 if pos_x < ninho_x else -1)
            dir_ny = 0 if pos_y == ninho_y else (1 if pos_y < ninho_y else -1)

            return f"CARGA_{obs_dados['no_ninho']}_{dir_nx}_{dir_ny}_P{paredes}_L{ultima_acao}"

        else:
            pos_recurso = obs_dados.get("pos_recurso_proximo")
            if pos_recurso:
                rec_x, rec_y = pos_recurso
                dir_rx = 0 if pos_x == rec_x else (1 if pos_x < rec_x else -1)
                dir_ry = 0 if pos_y == rec_y else (1 if pos_y < rec_y else -1)
                em_cima = (dir_rx == 0 and dir_ry == 0)
            else:
                dir_rx, dir_ry = 0, 0
                em_cima = False

            return f"BUSCA_{em_cima}_{dir_rx}_{dir_ry}_P{paredes}_L{ultima_acao}"

    def executar(self, ambiente: Ambiente) -> None:
        # 1. Observar estado atual (S_t)
        acoes = ["CIMA", "BAIXO", "ESQ", "DIR", "APANHAR", "DEPOSITAR"]

        if self.modo == ModoOperacao.ALEATORIO:
            # Inclui as ações de jogo!
            ambiente.agir(Acao(tipo=random.choice(acoes)), self)
            return

        obs = ambiente.observacaoPara(self)
        estado_atual = self._traduzir_estado(obs.dados)


        if estado_atual not in self.q_table:
            self.q_table[estado_atual] = {a: 0.0 for a in acoes}

        # 2. Atualizar Q-Table do passo anterior
        if self.modo == ModoOperacao.APRENDIZAGEM and self.estado_anterior is not None:
            max_q_futuro = max(self.q_table[estado_atual].values())
            q_atual = self.q_table[self.estado_anterior][self.acao_anterior]

            # A Fórmula Mágica do Q-Learning: Q(s,a) = Q(s,a) + alpha * [R + gamma * max(Q(s',a')) - Q(s,a)]
            self.q_table[self.estado_anterior][self.acao_anterior] = q_atual + self.alpha * (self.recompensa_anterior + self.gamma * max_q_futuro - q_atual)

        # 3. Deliberar / Selecionar Ação (Epsilon-Greedy)
        if self.modo == ModoOperacao.APRENDIZAGEM and random.random() < self.epsilon:
            escolha = random.choice(acoes) # Explora
        else:
            # Explora a melhor ação conhecida (quebra empates aleatoriamente)
            max_q = max(self.q_table[estado_atual].values())
            melhores = [a for a, q in self.q_table[estado_atual].items() if q == max_q]
            escolha = random.choice(melhores)

        accao = Acao(tipo=escolha)

        # 4. Executar e registar para o próximo turno
        recompensa = ambiente.agir(accao, self)

        self.estado_anterior = estado_atual
        self.acao_anterior = escolha
        self.recompensa_anterior = recompensa

    def fim_episodio(self):
        """Reduz a taxa de exploração no fim de cada tentativa."""
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def save(self):
        with open(self.ficheiro_modelo, 'wb') as f:
            pickle.dump(self.q_table, f)

    def load(self):
        if os.path.exists(self.ficheiro_modelo):
            with open(self.ficheiro_modelo, 'rb') as f:
                self.q_table = pickle.load(f)
        else:
            print(f"Aviso: Não encontrei o ficheiro {self.ficheiro_modelo}. A usar Q-Table vazia.")