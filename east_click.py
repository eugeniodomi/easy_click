import pygame
import random

# --- 1. CONFIG INICIAL ---
pygame.init()

# Setup da janela
LARGURA, ALTURA = 800, 600
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Alvo Rápido")

# Cores em formato RGB
PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)
VERMELHO = (255, 0, 0)
VERDE = (0, 255, 0)
AZUL = (0, 100, 255)
AMARELO = (255, 255, 0)

# Para controlar a velocidade do jogo
relogio = pygame.time.Clock()
FPS = 60

# Configuração da fonte para exibir texto na tela
FONTE_TITULO = pygame.font.Font(None, 74)
FONTE = pygame.font.Font(None, 50)
FONTE_PEQUENA = pygame.font.Font(None, 35)

# Nome do arquivo que guardará o recorde
ARQUIVO_HIGHSCORE = "highscore.txt"

# --- FUNÇÕES AUXILIARES ---
# Função para desenhar texto na tela com diferentes alinhamentos
def desenhar_texto(texto, fonte, cor, superficie, x, y, alinhamento="centro"):
    textobj = fonte.render(texto, True, cor)
    textrect = textobj.get_rect()
    if alinhamento == "centro":
        textrect.center = (x, y)
    elif alinhamento == "topo_esquerda":
        textrect.topleft = (x, y)
    superficie.blit(textobj, textrect)

# Função para resetar e configurar as variáveis de um nível
def iniciar_nivel():
    global pontos, alvos, tempo_inicio, ultimo_spawn, TEMPO_PARA_SPAWN, raio_min, raio_max
    pontos = 0
    alvos = []
    tempo_inicio = pygame.time.get_ticks()
    ultimo_spawn = tempo_inicio
    dificuldade = DIFICULDADES[nivel]
    TEMPO_PARA_SPAWN = dificuldade['spawn']
    raio_min = dificuldade['raio_min']
    raio_max = dificuldade['raio_max']

# Funções para ler e escrever a pontuação máxima no arquivo
def carregar_high_score():
    try:
        with open(ARQUIVO_HIGHSCORE, 'r') as f:
            return int(f.read())
    except (FileNotFoundError, ValueError):
        return 0

def salvar_high_score(score):
    with open(ARQUIVO_HIGHSCORE, 'w') as f:
        f.write(str(score))

# --- 2. VARIÁVEIS DO JOGO ---
# Variável que controla a tela atual do jogo
estado_jogo = "menu_inicial"
# Nível atual
nivel = 1
# Metas de pontos para cada nível
METAS = {1: 15, 2: 25}
# Configurações de dificuldade (velocidade de spawn e tamanho dos alvos)
DIFICULDADES = {
    1: {'spawn': 1000, 'raio_min': 30, 'raio_max': 60},
    2: {'spawn': 750, 'raio_min': 20, 'raio_max': 45}
}

# Alvos que aparecem na tela
alvos = []

# Lógica de "spawn" dos alvos
TEMPO_PARA_SPAWN = None
ultimo_spawn = 0 # Guarda o tempo do último alvo criado
raio_min, raio_max = 0, 0

# Pontuação
pontos = 0

# Variáveis para o temporizador do nível
TEMPO_DO_NIVEL = 30000  # 30 segundos em milissegundos
tempo_inicio = 0  # Registra quando o jogo começou

# Carrega o recorde salvo no arquivo
high_score = carregar_high_score()

# Variáveis para controlar o menu navegável
opcoes_menu = ["Iniciar Jogo", "Regras", "Sobre", "Recordes", "Sair"]
opcao_selecionada = 0

# --- 3. O CORAÇÃO DO JOGO (LOOP PRINCIPAL) ---
rodando = True
while rodando:
    relogio.tick(FPS)

    # Lógica para a tela de Menu Inicial
    if estado_jogo == "menu_inicial":
        TELA.fill(PRETO)
        desenhar_texto("Alvo Rápido", FONTE_TITULO, BRANCO, TELA, LARGURA // 2, ALTURA // 4 - 50)
        # Desenha as opções do menu, destacando a selecionada
        for i, opcao in enumerate(opcoes_menu):
            cor = AMARELO if i == opcao_selecionada else BRANCO
            desenhar_texto(opcao, FONTE, cor, TELA, LARGURA // 2, ALTURA // 2 + i * 60)
        
        # Cuida dos inputs do jogador para navegar no menu
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rodando = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    opcao_selecionada = (opcao_selecionada - 1) % len(opcoes_menu)
                elif event.key == pygame.K_DOWN:
                    opcao_selecionada = (opcao_selecionada + 1) % len(opcoes_menu)
                elif event.key == pygame.K_RETURN:
                    opcao_escolhida = opcoes_menu[opcao_selecionada]
                    if opcao_escolhida == "Iniciar Jogo":
                        nivel = 1
                        iniciar_nivel()
                        estado_jogo = "jogando"
                    elif opcao_escolhida == "Regras":
                        estado_jogo = "regras"
                    elif opcao_escolhida == "Sobre":
                        estado_jogo = "sobre"
                    elif opcao_escolhida == "Recordes":
                        estado_jogo = "recordes"
                    elif opcao_escolhida == "Sair":
                        rodando = False

    # Lógica para a tela de Regras
    elif estado_jogo == "regras":
        TELA.fill(PRETO)
        desenhar_texto("Regras", FONTE_TITULO, BRANCO, TELA, LARGURA // 2, 100)
        desenhar_texto("- Clique nos alvos para pontuar.", FONTE_PEQUENA, BRANCO, TELA, 100, 200, "topo_esquerda")
        desenhar_texto("- Alvos Vermelhos: +1 ponto", FONTE_PEQUENA, VERMELHO, TELA, 120, 250, "topo_esquerda")
        desenhar_texto("- Alvos Verdes: +5 pontos (Bônus!)", FONTE_PEQUENA, VERDE, TELA, 120, 300, "topo_esquerda")
        desenhar_texto("- Alvos Azuis: -3 pontos (Penalidade!)", FONTE_PEQUENA, AZUL, TELA, 120, 350, "topo_esquerda")
        desenhar_texto("- Cumpra a meta de pontos antes do tempo acabar.", FONTE_PEQUENA, BRANCO, TELA, 100, 400, "topo_esquerda")
        desenhar_texto("Pressione ESC para voltar ao menu", FONTE, AMARELO, TELA, LARGURA // 2, ALTURA - 50)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rodando = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                estado_jogo = "menu_inicial"

    # Lógica para a tela Sobre
    elif estado_jogo == "sobre":
        TELA.fill(PRETO)
        desenhar_texto("Sobre", FONTE_TITULO, BRANCO, TELA, LARGURA // 2, 100)
        desenhar_texto("Este projeto foi desenvolvido por:", FONTE_PEQUENA, BRANCO, TELA, LARGURA // 2, 220)
        desenhar_texto("Eugenio Domingues", FONTE, AMARELO, TELA, LARGURA // 2, 280)
        desenhar_texto("como trabalho de Linguagem de Programação Aplicada", FONTE_PEQUENA, BRANCO, TELA, LARGURA // 2, 350)
        desenhar_texto("para a Uninter.", FONTE_PEQUENA, BRANCO, TELA, LARGURA // 2, 390)
        desenhar_texto("Pressione ESC para voltar ao menu", FONTE, AMARELO, TELA, LARGURA // 2, ALTURA - 50)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rodando = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                estado_jogo = "menu_inicial"

    # Lógica para a tela de Recordes
    elif estado_jogo == "recordes":
        TELA.fill(PRETO)
        desenhar_texto("Recorde", FONTE_TITULO, BRANCO, TELA, LARGURA // 2, 150)
        desenhar_texto(str(high_score), FONTE_TITULO, AMARELO, TELA, LARGURA // 2, ALTURA // 2)
        desenhar_texto("Pressione ESC para voltar ao menu", FONTE, AMARELO, TELA, LARGURA // 2, ALTURA - 50)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rodando = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                estado_jogo = "menu_inicial"

    # Lógica principal do jogo
    elif estado_jogo == "jogando":
        # --- 4. CUIDANDO DOS INPUTS DO JOGADOR ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rodando = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos_mouse = pygame.mouse.get_pos()
                for alvo_dict in alvos[:]:
                    if alvo_dict['rect'].collidepoint(pos_mouse):
                        tipo_alvo = alvo_dict['tipo']
                        if tipo_alvo == 'normal': pontos += 1
                        elif tipo_alvo == 'bonus': pontos += 5
                        elif tipo_alvo == 'penalidade': pontos -= 3
                        pontos = max(0, pontos)
                        alvos.remove(alvo_dict)

        # --- 5. A LÓGICA ---
        tempo_agora = pygame.time.get_ticks()
        # Lógica do novo alvo
        if tempo_agora - ultimo_spawn > TEMPO_PARA_SPAWN:
            raio_alvo = random.randint(raio_min, raio_max)
            pos_x = random.randint(raio_alvo, LARGURA - raio_alvo)
            pos_y = random.randint(raio_alvo, ALTURA - raio_alvo)
            rect = pygame.Rect(pos_x - raio_alvo, pos_y - raio_alvo, raio_alvo * 2, raio_alvo * 2)
            chance = random.random()
            if chance < 0.7: tipo, cor = 'normal', VERMELHO
            elif chance < 0.85: tipo, cor = 'bonus', VERDE
            else: tipo, cor = 'penalidade', AZUL
            novo_alvo = {'rect': rect, 'tipo': tipo, 'cor': cor}
            alvos.append(novo_alvo)
            ultimo_spawn = tempo_agora
        
        # Lógica do temporizador
        tempo_decorrido = tempo_agora - tempo_inicio
        tempo_restante = (TEMPO_DO_NIVEL - tempo_decorrido) // 1000 # Converte para segundos
        # Garante que o tempo não fique negativo na tela
        if tempo_restante < 0:
            tempo_restante = 0

        # Verifica a condição de vitória ou derrota
        if pontos >= METAS[nivel]:
            if nivel == 1:
                nivel = 2
                iniciar_nivel()
            else:
                if pontos > high_score:
                    high_score = pontos
                    salvar_high_score(high_score)
                estado_jogo = "vitoria"
        # Verifica se o tempo acabou para encerrar o jogo
        elif tempo_decorrido >= TEMPO_DO_NIVEL:
            if pontos > high_score:
                high_score = pontos
                salvar_high_score(high_score)
            estado_jogo = "game_over"

        # --- 6. DESENHANDO NA TELA ---
        TELA.fill(PRETO)
        # Desenha um círculo para cada alvo na nossa lista
        for alvo_dict in alvos:
            pygame.draw.circle(TELA, alvo_dict['cor'], alvo_dict['rect'].center, alvo_dict['rect'].width // 2)
        # Desenha o placar de pontos
        texto_pontos_surface = FONTE.render(f"Pontos: {pontos} / {METAS[nivel]}", True, BRANCO)
        TELA.blit(texto_pontos_surface, (10, 10))
        # Desenha o temporizador
        texto_tempo_surface = FONTE.render(f"Tempo: {tempo_restante}", True, BRANCO)
        pos_x_tempo = LARGURA - texto_tempo_surface.get_width() - 10
        TELA.blit(texto_tempo_surface, (pos_x_tempo, 10))

    # Lógica para a tela de vitória
    elif estado_jogo == "vitoria":
        TELA.fill(PRETO)
        desenhar_texto("VOCÊ VENCEU!", FONTE_TITULO, VERDE, TELA, LARGURA // 2, ALTURA // 3)
        desenhar_texto(f"Pontuação Final: {pontos}", FONTE, BRANCO, TELA, LARGURA // 2, ALTURA // 2)
        desenhar_texto(f"Recorde: {high_score}", FONTE, AMARELO, TELA, LARGURA // 2, ALTURA // 2 + 50)
        desenhar_texto("Pressione ESPAÇO para jogar de novo", FONTE, BRANCO, TELA, LARGURA // 2, ALTURA * 5 // 6)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rodando = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                estado_jogo = "menu_inicial"

    # Lógica para a tela de game over
    elif estado_jogo == "game_over":
        TELA.fill(PRETO)
        desenhar_texto("GAME OVER", FONTE_TITULO, VERMELHO, TELA, LARGURA // 2, ALTURA // 3)
        desenhar_texto(f"Sua pontuação: {pontos}", FONTE, BRANCO, TELA, LARGURA // 2, ALTURA // 2)
        desenhar_texto(f"Recorde: {high_score}", FONTE, AMARELO, TELA, LARGURA // 2, ALTURA // 2 + 50)
        desenhar_texto("Pressione ESPAÇO para tentar novamente", FONTE, BRANCO, TELA, LARGURA // 2, ALTURA * 5 // 6)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rodando = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                estado_jogo = "menu_inicial"

    pygame.display.flip()

# --- 7. TUDO ACABOU ---
pygame.quit()