import time
import csv
import matplotlib.pyplot as plt

from Core.Visualizador import Visualizador
from Core.definicoes import ModoOperacao
from Core.MotorSimulacao import MotorDeSimulacao

from simulacoes.farol.Ambiente import AmbienteFarol
from simulacoes.farol.Agente import AgenteFarol
from simulacoes.recolecao.Ambiente import AmbienteRecolecao
from simulacoes.recolecao.Agente import AgenteRecolecao


# ==========================================
# FUNÇÕES AUXILIARES (GRÁFICOS E CSV)
# ==========================================

def exportar_csv(nome_ficheiro, dados, cabecalhos):
    with open(nome_ficheiro, "w", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=cabecalhos)
        escritor.writeheader()
        escritor.writerows(dados)
    print(f"[SUCESSO] Dados exportados para '{nome_ficheiro}'.")

def gerar_grafico(historico, x_key, y_key, titulo, y_label, nome_ficheiro):
    x = [h[x_key] for h in historico]
    y = [h[y_key] for h in historico]
    plt.figure(figsize=(10, 5))
    plt.plot(x, y, label=y_label, color='blue' if 'Recursos' in y_label else 'red')
    plt.title(titulo)
    plt.xlabel("Episódio")
    plt.ylabel(y_label)
    plt.grid(True)
    plt.legend()
    plt.savefig(nome_ficheiro)
    plt.show()


# ==========================================
# MÓDULO: FAROL
# ==========================================

def treino_farol():
    print("\n--- INICIANDO TREINO: FAROL (1000 Episódios) ---")

    # 1. Setup do Ambiente e Agente
    amb = AmbienteFarol(largura=20, altura=20)
    agente = AgenteFarol("AgenteTreinado", ModoOperacao.APRENDIZAGEM)
    agente.ficheiro_modelo = "modelo_farol.pkl"

    # 2. Configurar o Motor
    motor = MotorDeSimulacao()
    motor._ambiente = amb
    motor._agentes = [agente]
    motor._passos_maximos = 200

    # 3. Mandar o motor treinar!
    motor.executa_episodios(1000)

    # 4. Guardar modelo e gerar relatórios
    agente.save()
    exportar_csv("curva_farol.csv", motor.historico, ["episodio", "resultado"])
    gerar_grafico(motor.historico, "episodio", "resultado", "Eficiência Farol (Menos passos = Melhor)", "Passos", "grafico_farol.png")


def teste_farol(modo):
    print(f"\n--- INICIANDO TESTE VISUAL: FAROL ({modo.name}) ---")

    # 1. Setup
    amb = AmbienteFarol(largura=20, altura=20)
    agente = AgenteFarol("AgenteTeste", modo=modo)
    agente.ficheiro_modelo = "modelo_farol.pkl"

    if modo == ModoOperacao.TESTE:
        agente.load()

    # Prepara o mapa e o agente (o reset() do Farol coloca o agente numa posição aleatória)
    amb.posicoes_agentes[agente] = (0, 0) # Registo inicial
    amb.reset()

    # 2. Configurar o Motor com Visualizador
    motor = MotorDeSimulacao()
    motor._ambiente = amb
    motor._agentes = [agente]
    motor._passos_maximos = 200

    vis = Visualizador(amb)
    motor.visualizador = vis
    motor.delay = 0.05

    # 3. Mandar o motor correr 1 episódio visual
    motor.executa()

    if amb.objetivo_alcancado():
        print(f"Objetivo alcançado em {motor._passo_atual} passos!")
    else:
        print("O agente não conseguiu chegar ao farol a tempo.")


# ==========================================
# MÓDULO: RECOLEÇÃO
# ==========================================

def configurar_ambiente_recolecao():
    """Função utilitária para garantir que o mapa de teste é IGUAL ao de treino"""
    amb = AmbienteRecolecao(largura=20, altura=20, pos_ninho=(10, 10))
    amb.obstaculos = [(8, 9), (8, 10), (8, 11), (12, 9), (12, 10), (12, 11)]
    return amb


def treino_recolecao():
    print("\n--- INICIANDO TREINO: RECOLEÇÃO (1000 Episódios) ---")

    # 1. Setup
    amb = configurar_ambiente_recolecao()
    agentes = [AgenteRecolecao(f"RL_{i}", ModoOperacao.APRENDIZAGEM) for i in range(1, 3)]
    for i, a in enumerate(agentes):
        a.ficheiro_modelo = f"modelo_recolecao_{i}.pkl"

    # 2. Configurar o Motor
    motor = MotorDeSimulacao()
    motor._ambiente = amb
    motor._agentes = agentes
    motor._passos_maximos = 300

    # 3. Treinar
    motor.executa_episodios(1000)

    # 4. Guardar resultados
    for a in agentes:
        a.save()

    exportar_csv("curva_recolecao.csv", motor.historico, ["episodio", "resultado"])
    gerar_grafico(motor.historico, "episodio", "resultado", "Aprendizagem Recoleção (Mais recursos = Melhor)", "Recursos Depositados", "grafico_recolecao.png")


def teste_recolecao(modo):
    print(f"\n--- INICIANDO TESTE VISUAL: RECOLEÇÃO ({modo.name}) ---")

    # 1. Setup
    amb = configurar_ambiente_recolecao()
    agentes = [AgenteRecolecao(f"Teste_{i}", modo=modo) for i in range(1, 3)]

    for i, a in enumerate(agentes):
        if modo == ModoOperacao.TESTE:
            a.ficheiro_modelo = f"modelo_recolecao_{i}.pkl"
            a.load()
        amb.posicoes_agentes[a] = (10, 10) # Nascem no ninho

    amb.reset()

    # 2. Configurar o Motor com Visualizador
    motor = MotorDeSimulacao()
    motor._ambiente = amb
    motor._agentes = agentes
    motor._passos_maximos = 300

    vis = Visualizador(amb)
    motor.visualizador = vis
    motor.delay = 0.05

    # 3. Mandar o motor correr o teste visual
    motor.executa()

    print(f"Simulação terminada! Recursos totais depositados: {amb.recursos_totais_depositados}")


# ==========================================
# MENU PRINCIPAL
# ==========================================

def main():
    while True:
        print("\n" + "="*35)
        print("        MENU DE SIMULAÇÃO")
        print("="*35)
        print("1. Treinar Agente FAROL")
        print("2. Visualizar FAROL (Inteligente)")
        print("3. Visualizar FAROL (Aleatório)")
        print("-" * 35)
        print("4. Treinar Agentes RECOLEÇÃO")
        print("5. Visualizar RECOLEÇÃO (Inteligente)")
        print("6. Visualizar RECOLEÇÃO (Aleatório)")
        print("-" * 35)
        print("7. Sair")
        print("="*35)

        escolha = input("Escolha uma opção: ")

        if escolha == "1":
            treino_farol()
        elif escolha == "2":
            teste_farol(ModoOperacao.TESTE)
        elif escolha == "3":
            teste_farol(ModoOperacao.ALEATORIO)
        elif escolha == "4":
            treino_recolecao()
        elif escolha == "5":
            teste_recolecao(ModoOperacao.TESTE)
        elif escolha == "6":
            teste_recolecao(ModoOperacao.ALEATORIO)
        elif escolha == "7":
            print("A encerrar o simulador...")
            break
        else:
            print("Opção inválida. Tenta novamente.")

if __name__ == "__main__":
    main()