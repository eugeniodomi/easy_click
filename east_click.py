import pygame
import random
import json

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

# Nome do arquivo de recordes
ARQUIVO_HIGHSCORE = "highscores.json"

# --- FUNÇÕES AUXILIARES ---
def desenhar_texto(texto, fonte, cor, superficie, x, y, alinhamento="centro"):
    textobj = fonte.render(texto, True, cor)
    textrect = textobj.get_rect()
    if alinhamento == "centro":
        textrect.center = (x, y)
    elif alinhamento == "topo_esquerda":
        textrect.topleft = (x, y)
    superficie.blit(textobj, textrect)

def iniciar_nivel():
    global pontos, alvos, tempo_inicio, ultimo_spawn, TEMPO_PARA_SPAWN, raio_min, raio_max, combo_atual
    pontos = 0
    alvos = []
    tempo_inicio = pygame.time.get_ticks()
    ultimo_spawn = tempo_inicio
    dificuldade = DIFICULDADES[nivel]
    TEMPO_PARA_SPAWN = dificuldade['spawn']
    raio_min = dificuldade['raio_min']
    raio_max = dificuldade['raio_max']
    combo_atual = 0

def carregar_high_scores():
    try:
        with open(ARQUIVO_HIGHSCORE, 'r') as f:
            scores = json.load(f)
            scores.sort(key=lambda item: item[1], reverse=True)
            return scores
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def salvar_high_scores(scores):
    with open(ARQUIVO_HIGHSCORE, 'w') as f:
        json.dump(scores, f, indent=4)

def adicionar_high_score(nome, score, scores):
    scores.append([nome, score])
    scores.sort(key=lambda item: item[1], reverse=True)
    return scores[:5]

# --- 2. VARIÁVEIS DO JOGO ---
estado_jogo = "menu_inicial"
nivel = 1
# Meta de pontos para cada nível
METAS = {1: 15, 2: 25, 3: 40}
# Configuração de dificuldade para cada nível
DIFICULDADES = {
    1: {'spawn': 1000, 'raio_min': 30, 'raio_max': 60},
    2: {'spawn': 750, 'raio_min': 20, 'raio_max': 45},
    3: {'spawn': 500, 'raio_min': 15, 'raio_max': 35}
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
TEMPO_DO_NIVEL = 30000 # 30 segundos em milissegundos
tempo_inicio = 0 # Registra quando o jogo começou
high_scores = carregar_high_scores()
opcoes_menu = ["Iniciar Jogo", "Regras", "Sobre", "Recordes", "Sair"]
opcao_selecionada = 0
combo_atual = 0
pontos_base_final = 0
bonus_tempo_final = 0
nome_jogador = ""
pontos_finais_para_salvar = 0
confirmando_reset = False

# --- 3. O CORAÇÃO DO JOGO (LOOP PRINCIPAL) ---
rodando = True
while rodando:
    relogio.tick(FPS)
    
    # Gerencia a tela de Menu Inicial
    if estado_jogo == "menu_inicial":
        TELA.fill(PRETO)
        desenhar_texto("Alvo Rápido", FONTE_TITULO, BRANCO, TELA, LARGURA // 2, ALTURA // 4 - 50)
        for i, opcao in enumerate(opcoes_menu):
            cor = AMARELO if i == opcao_selecionada else BRANCO
            desenhar_texto(opcao, FONTE, cor, TELA, LARGURA // 2, ALTURA // 2 + i * 60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: rodando = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP: opcao_selecionada = (opcao_selecionada - 1) % len(opcoes_menu)
                elif event.key == pygame.K_DOWN: opcao_selecionada = (opcao_selecionada + 1) % len(opcoes_menu)
                elif event.key == pygame.K_RETURN:
                    opcao_escolhida = opcoes_menu[opcao_selecionada]
                    if opcao_escolhida == "Iniciar Jogo":
                        nivel = 1
                        iniciar_nivel()
                        estado_jogo = "jogando"
                    elif opcao_escolhida == "Regras": estado_jogo = "regras"
                    elif opcao_escolhida == "Sobre": estado_jogo = "sobre"
                    elif opcao_escolhida == "Recordes": estado_jogo = "recordes"
                    elif opcao_escolhida == "Sair": rodando = False
    
    # Gerencia a tela de Regras
    elif estado_jogo == "regras":
        TELA.fill(PRETO)
        desenhar_texto("Regras", FONTE_TITULO, BRANCO, TELA, LARGURA // 2, 100)
        desenhar_texto("- Clique nos alvos para pontuar.", FONTE_PEQUENA, BRANCO, TELA, 100, 200, "topo_esquerda")
        desenhar_texto("- Acertos em sequência aumentam seu COMBO.", FONTE_PEQUENA, BRANCO, TELA, 100, 250, "topo_esquerda")
        desenhar_texto("- A pontuação é multiplicada pelo combo!", FONTE_PEQUENA, AMARELO, TELA, 100, 300, "topo_esquerda")
        desenhar_texto("- Errar um clique ou acertar um alvo azul ZERA o combo.", FONTE_PEQUENA, BRANCO, TELA, 100, 350, "topo_esquerda")
        desenhar_texto("Pressione ESC para voltar ao menu", FONTE, AMARELO, TELA, LARGURA // 2, ALTURA - 50)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: rodando = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: estado_jogo = "menu_inicial"
    
    # Gerencia a tela Sobre
    elif estado_jogo == "sobre":
        TELA.fill(PRETO)
        desenhar_texto("Sobre", FONTE_TITULO, BRANCO, TELA, LARGURA // 2, 100)
        desenhar_texto("Este projeto foi desenvolvido por:", FONTE_PEQUENA, BRANCO, TELA, LARGURA // 2, 220)
        desenhar_texto("Eugenio Domingues", FONTE, AMARELO, TELA, LARGURA // 2, 280)
        desenhar_texto("como trabalho de Linguagem de Programação Aplicada", FONTE_PEQUENA, BRANCO, TELA, LARGURA // 2, 350)
        desenhar_texto("para a Uninter.", FONTE_PEQUENA, BRANCO, TELA, LARGURA // 2, 390)
        desenhar_texto("Pressione ESC para voltar ao menu", FONTE, AMARELO, TELA, LARGURA // 2, ALTURA - 50)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: rodando = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: estado_jogo = "menu_inicial"

    # Gerencia a tela de Recordes
    elif estado_jogo == "recordes":
        TELA.fill(PRETO)
        if not confirmando_reset:
            desenhar_texto("Recordes", FONTE_TITULO, BRANCO, TELA, LARGURA // 2, 80)
            if not high_scores:
                desenhar_texto("Nenhum recorde salvo ainda!", FONTE, BRANCO, TELA, LARGURA // 2, ALTURA // 2)
            else:
                for i, (nome, score) in enumerate(high_scores):
                    desenhar_texto(f"{i+1}. {nome}", FONTE, BRANCO, TELA, LARGURA // 4, 180 + i * 50, "topo_esquerda")
                    desenhar_texto(str(score), FONTE, AMARELO, TELA, LARGURA * 3 // 4, 180 + i * 50, "centro")
            desenhar_texto("Pressione R para Resetar", FONTE_PEQUENA, VERMELHO, TELA, LARGURA // 2, ALTURA - 100)
            desenhar_texto("Pressione ESC para voltar ao menu", FONTE, AMARELO, TELA, LARGURA // 2, ALTURA - 50)
        else:
            desenhar_texto("Tem certeza, meu chapa?", FONTE, AMARELO, TELA, LARGURA // 2, ALTURA // 3)
            desenhar_texto("[S] Sim / [N] Não", FONTE, BRANCO, TELA, LARGURA // 2, ALTURA // 2)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: rodando = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    confirmando_reset = False
                    estado_jogo = "menu_inicial"
                if not confirmando_reset:
                    if event.key == pygame.K_r: confirmando_reset = True
                else:
                    if event.key == pygame.K_s:
                        high_scores = []
                        salvar_high_scores(high_scores)
                        confirmando_reset = False
                    elif event.key == pygame.K_n: confirmando_reset = False
    
    # Gerencia a tela de Inserir Nome
    elif estado_jogo == "inserir_nome":
        TELA.fill(PRETO)
        desenhar_texto("NOVO RECORDE!", FONTE_TITULO, AMARELO, TELA, LARGURA // 2, ALTURA // 4)
        desenhar_texto(f"Sua pontuação: {pontos_finais_para_salvar}", FONTE, BRANCO, TELA, LARGURA // 2, ALTURA // 2 - 50)
        desenhar_texto("Digite seu nome (6 caracteres):", FONTE_PEQUENA, BRANCO, TELA, LARGURA // 2, ALTURA // 2 + 20)
        texto_nome = nome_jogador + "_" * (6 - len(nome_jogador))
        desenhar_texto(texto_nome, FONTE_TITULO, BRANCO, TELA, LARGURA // 2, ALTURA // 2 + 100)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: rodando = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and len(nome_jogador) > 0:
                    high_scores = adicionar_high_score(nome_jogador, pontos_finais_para_salvar, high_scores)
                    salvar_high_scores(high_scores)
                    estado_jogo = "recordes"
                elif event.key == pygame.K_BACKSPACE: nome_jogador = nome_jogador[:-1]
                elif len(nome_jogador) < 6 and event.unicode: nome_jogador += event.unicode
    
    # Gerencia a tela de Transição de Nível
    elif estado_jogo == "transicao_nivel":
        TELA.fill(PRETO)
        desenhar_texto(f"Nível {nivel + 1}", FONTE_TITULO, BRANCO, TELA, LARGURA // 2, ALTURA // 3)
        desenhar_texto(f"Meta: {METAS[nivel + 1]} pontos", FONTE, BRANCO, TELA, LARGURA // 2, ALTURA // 2)
        desenhar_texto("Pressione ESPAÇO para continuar", FONTE, AMARELO, TELA, LARGURA // 2, ALTURA * 2 // 3)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rodando = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                nivel += 1
                iniciar_nivel()
                estado_jogo = "jogando"

    # Lógica principal quando o jogo está rodando
    elif estado_jogo == "jogando":
        # --- 4. CUIDANDO DOS INPUTS DO JOGADOR ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT: rodando = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos_mouse = pygame.mouse.get_pos()
                acertou_alvo = False
                for alvo_dict in alvos[:]:
                    if alvo_dict['rect'].collidepoint(pos_mouse):
                        acertou_alvo = True
                        tipo_alvo = alvo_dict['tipo']
                        if tipo_alvo == 'normal' or tipo_alvo == 'bonus':
                            combo_atual += 1
                            pontos_base = 5 if tipo_alvo == 'bonus' else 1
                            pontos += pontos_base * combo_atual
                        elif tipo_alvo == 'penalidade':
                            combo_atual = 0
                            pontos -= 3
                        pontos = max(0, pontos) # Garante que a pontuação não seja negativa
                        alvos.remove(alvo_dict)
                        break
                if not acertou_alvo: combo_atual = 0

        # --- 5. A LÓGICA ---

        # Lógica do novo alvo
        tempo_agora = pygame.time.get_ticks()
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
        if tempo_restante < 0: tempo_restante = 0

        # Verifica se a meta do nível foi atingida ou se o tempo acabou
        if pontos >= METAS[nivel]:
            if nivel < 3: # Se passou do nível 1 ou 2, vai para a transição
                estado_jogo = "transicao_nivel"
            else: # Se passou do nível 3 (final), calcula a pontuação e vai para a vitória/recorde
                pontos_base_final = pontos
                bonus_tempo_final = tempo_restante * 10
                pontos_finais_para_salvar = pontos + bonus_tempo_final
                if len(high_scores) < 5 or pontos_finais_para_salvar > (high_scores[-1][1] if high_scores else 0):
                    estado_jogo = "inserir_nome"
                else:
                    estado_jogo = "vitoria"

        elif tempo_decorrido >= TEMPO_DO_NIVEL: # Se o tempo acabar em qualquer nível
            pontos_finais_para_salvar = pontos
            if len(high_scores) < 5 or pontos_finais_para_salvar > (high_scores[-1][1] if high_scores else 0):
                estado_jogo = "inserir_nome"
            else:
                estado_jogo = "game_over"

        # --- 6. DESENHANDO NA TELA ---
        TELA.fill(PRETO)
        
        # Desenha um círculo para cada alvo 
        for alvo_dict in alvos: pygame.draw.circle(TELA, alvo_dict['cor'], alvo_dict['rect'].center, alvo_dict['rect'].width // 2)
        
        # Desenhar o placar de pontos
        texto_pontos_surface = FONTE.render(f"Pontos: {pontos} / {METAS[nivel]}", True, BRANCO)
        TELA.blit(texto_pontos_surface, (10, 10)) 
        
        # Desenhar o temporizador
        texto_tempo_surface = FONTE.render(f"Tempo: {tempo_restante}", True, BRANCO)
        pos_x_tempo = LARGURA - texto_tempo_surface.get_width() - 10
        TELA.blit(texto_tempo_surface, (pos_x_tempo, 10)) # Posiciona o texto no canto superior direito
        
        # Desenha o combo na tela
        if combo_atual > 1: desenhar_texto(f"{combo_atual}x COMBO!", FONTE, AMARELO, TELA, LARGURA // 2, ALTURA - 40)

    # Gerencia a tela de Vitória
    elif estado_jogo == "vitoria":
        TELA.fill(PRETO)
        desenhar_texto("VOCÊ VENCEU!", FONTE_TITULO, VERDE, TELA, LARGURA // 2, ALTURA // 4)
        desenhar_texto(f"Pontos Base: {pontos_base_final}", FONTE_PEQUENA, BRANCO, TELA, LARGURA // 2, ALTURA // 2 - 20)
        desenhar_texto(f"Bônus de Tempo: +{bonus_tempo_final}", FONTE_PEQUENA, BRANCO, TELA, LARGURA // 2, ALTURA // 2 + 20)
        pontos_totais = pontos_base_final + bonus_tempo_final
        desenhar_texto(f"Pontuação Final: {pontos_totais}", FONTE, AMARELO, TELA, LARGURA // 2, ALTURA // 2 + 70)
        desenhar_texto("Pressione ESPAÇO para jogar de novo", FONTE_PEQUENA, BRANCO, TELA, LARGURA // 2, ALTURA * 5 // 6)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: rodando = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE: estado_jogo = "menu_inicial"

    # Gerencia a tela de Game Over
    elif estado_jogo == "game_over":
        TELA.fill(PRETO)
        desenhar_texto("GAME OVER", FONTE_TITULO, VERMELHO, TELA, LARGURA // 2, ALTURA // 3)
        desenhar_texto(f"Sua pontuação: {pontos}", FONTE, BRANCO, TELA, LARGURA // 2, ALTURA // 2)
        recorde_maximo = high_scores[0][1] if high_scores else 0
        desenhar_texto(f"Recorde: {recorde_maximo}", FONTE, AMARELO, TELA, LARGURA // 2, ALTURA // 2 + 50)
        desenhar_texto("Pressione ESPAÇO para tentar novamente", FONTE_PEQUENA, BRANCO, TELA, LARGURA // 2, ALTURA * 5 // 6)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: rodando = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE: estado_jogo = "menu_inicial"

    pygame.display.flip()

# --- 7. TUDO ACABOU ---
pygame.quit()