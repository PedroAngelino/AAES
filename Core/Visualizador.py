import tkinter as tk
from Core.Ambiente import Ambiente

class Visualizador:
    def __init__(self, ambiente: Ambiente, largura_px: int = 600, altura_px: int = 600):
        self.ambiente = ambiente
        self.root = tk.Tk()
        self.root.title("Simulador Multi-Agente")
        self.canvas = tk.Canvas(self.root, width=largura_px, height=altura_px, bg="white")
        self.canvas.pack()

        # Fator de escala (se a grelha for 20x20 e a janela 600x600, cada célula tem 30px)
        # Assumindo que o ambiente tem os atributos largura e altura
        self.escala_x = largura_px / getattr(ambiente, 'largura', 100)
        self.escala_y = altura_px / getattr(ambiente, 'altura', 100)

    def desenha_circulo(self, x, y, raio, cor):
        """Método auxiliar para desenhar no canvas."""
        px = (x + 0.5) * self.escala_x
        py = (y + 0.5) * self.escala_y
        r = raio * self.escala_x
        self.canvas.create_oval(px-r, py-r, px+r, py+r, fill=cor, outline="black")

    def desenha_quadrado(self, x, y, cor):
        """Método auxiliar para células de grelha."""
        px1 = x * self.escala_x
        py1 = y * self.escala_y
        px2 = px1 + self.escala_x
        py2 = py1 + self.escala_y
        self.canvas.create_rectangle(px1, py1, px2, py2, fill=cor, outline="gray")

    def renderizar(self):
        """Limpa o ecrã e desenha o estado atual do ambiente."""
        self.canvas.delete("all")

        # Bloqueia o ambiente apenas para leitura rápida
        with self.ambiente._lock:

            # --- Renderização Específica: Recoleção ---
            if hasattr(self.ambiente, 'mapa_recursos'):
                # Desenhar Ninho
                self.desenha_quadrado(self.ambiente.ninho[0], self.ambiente.ninho[1], cor="blue")

                # Desenhar Recursos
                for (rx, ry) in self.ambiente.mapa_recursos.keys():
                    self.desenha_quadrado(rx, ry, cor="green")

            # --- Renderização Específica: Farol ---
            if hasattr(self.ambiente, 'pos_farol'):
                self.desenha_circulo(self.ambiente.pos_farol[0], self.ambiente.pos_farol[1], 1.5, cor="yellow")

            # --- Renderização Comum: Obstáculos e Agentes ---
            for obs in self.ambiente.obstaculos:
                self.desenha_quadrado(obs[0], obs[1], cor="black")

            for agente, pos in self.ambiente.posicoes_agentes.items():
                # Desenhar agente (vermelho)
                self.desenha_circulo(pos[0], pos[1], 0.4 , cor="red")

        # Atualiza a janela do Tkinter
        self.root.update()