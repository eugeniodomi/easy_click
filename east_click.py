import pygame
import random
import json

# --- 1. CONFIG INICIAL ---
pygame.init()
pygame.mixer.init()

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

# --- 2. CARREGAMENTO DE ASSETS (IMAGENS E SONS) ---
# Carregan a imagem de fundo para o menu
imagem_menu = None
try:
    imagem_menu = pygame.image.load('imagens/menu_background.png').convert()
    imagem_menu = pygame.transform.scale(imagem_menu, (LARGURA, ALTURA))
except pygame.error as e:
    print(f"Aviso: Não foi possível carregar a imagem de fundo do menu: {e}")

# Carregan os arquivos de som e música
try:
    pygame.mixer.music.load('sons/musica_fundo.mp3')
    som_navegacao_menu = pygame.mixer.Sound('sons/navegacao.wav')
    som_selecao_menu = pygame.mixer.Sound('sons/selecao.wav')
    som_acerto_normal = pygame.mixer.Sound('sons/acerto_normal.wav')
    som_acerto_bonus = pygame.mixer.Sound('sons/acerto_bonus.wav')
    som_acerto_penalidade = pygame.mixer.Sound('sons/penalidade.wav')
    som_erro_clique = pygame.mixer.Sound('sons/erro.wav')
    som_level_up = pygame.mixer.Sound('sons/level_up.wav')
    som_vitoria = pygame.mixer.Sound('sons/vitoria.wav')
    som_game_over = pygame.mixer.Sound('sons/game_over.wav')
    pygame.mixer.music.set_volume(0.4)
except pygame.error as e:
    print(f"Erro ao carregar os sons: {e}")
    class DummySound:
        def play(self): pass
    som_navegacao_menu = som_selecao_menu = som_acerto_normal = som_acerto_bonus = som_acerto_penalidade = som_erro_clique = som_level_up = som_vitoria = som_game_over = DummySound()

# --- 3. FUNÇÕES AUXILIARES ---
def desenhar_texto(texto, fonte, cor, superficie, x, y, alinhamento="centro"):
    textobj = fonte.render(texto, True, cor)
    textrect = textobj.get_rect()
    if alinhamento == "centro":
        textrect.center = (x, y)
    elif alinhamento == "topo_esquerda":
        textrect.topleft = (x, y)
    superficie.blit(textobj, textrect)

def iniciar_nivel():
    global pontos, alvos, tempo_inicio, ultimo_spawn, TEMPO_PARA_SPAWN, raio_min, raio_max, combo_atual, tempo_aumento_dificuldade, modo_quase_impossivel
    pontos = 0
    alvos = []
    tempo_inicio = pygame.time.get_ticks()
    ultimo_spawn = tempo_inicio
    
    if modo_quase_impossivel:
        dificuldade = DIFICULDADES['quase_impossivel']
    else:
        dificuldade = DIFICULDADES[nivel]

    TEMPO_PARA_SPAWN = dificuldade['spawn']
    raio_min = dificuldade['raio_min']
    raio_max = dificuldade['raio_max']
    combo_atual = 0
    tempo_aumento_dificuldade = tempo_inicio + 10000

def carregar_high_scores():
    try:
        with open(ARQUIVO_HIGHSCORE, 'r') as f:
            scores = json.load(f)
            
            if not isinstance(scores, dict):
                scores = {}
            if 'comum' not in scores: scores['comum'] = []
            if 'impossivel' not in scores: scores['impossivel'] = []
            return scores
    except (FileNotFoundError, json.JSONDecodeError):
      
        return {'comum': [], 'impossivel': []}

def salvar_high_scores(scores):
    with open(ARQUIVO_HIGHSCORE, 'w') as f:
        json.dump(scores, f, indent=4)

def adicionar_high_score(nome, score, scores, modo):
    lista_recordes = scores.get(modo, [])
    lista_recordes.append([nome, score])
    lista_recordes.sort(key=lambda item: item[1], reverse=True)
    scores[modo] = lista_recordes[:5]
    return scores

# --- 4. VARIÁVEIS DO JOGO ---
estado_jogo = "menu_inicial"
nivel = 1
# Meta de pontos para cada nível
METAS = {1: 1500, 2: 3000, 3: 5000}
# Configuração de dificuldade para cada nível
DIFICULDADES = {
    1: {'spawn': 1000, 'raio_min': 30, 'raio_max': 60},
    2: {'spawn': 750, 'raio_min': 20, 'raio_max': 45},
    3: {'spawn': 500, 'raio_min': 15, 'raio_max': 35},
    'quase_impossivel': {'spawn': 400, 'raio_min': 10, 'raio_max': 25, 'velocidade_aumento': 30}
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
TEMPO_DO_NIVEL = 40000 # 40 segundos em milissegundos
tempo_inicio = 0 # Registra quando o jogo começou
high_scores = carregar_high_scores()
opcoes_menu = ["Iniciar Jogo", "Quase Impossível", "Regras", "Sobre", "Recordes", "Sair"]
opcao_selecionada = 0
combo_atual = 0
pontos_base_final = 0
bonus_tempo_final = 0
nome_jogador = ""
pontos_finais_para_salvar = 0
confirmando_reset = False
modo_quase_impossivel = False
tempo_aumento_dificuldade = 0
aba_recordes = 'comum'

# --- 5. O CORAÇÃO DO JOGO (LOOP PRINCIPAL) ---
rodando = True
pygame.mixer.music.play(-1)

while rodando:
    relogio.tick(FPS)
    
    # Gerencia a tela de Menu Inicial
    if estado_jogo == "menu_inicial":
        if imagem_menu:
            TELA.blit(imagem_menu, (0, 0))
        else:
            TELA.fill(PRETO)
            
        desenhar_texto("Alvo Rápido", FONTE_TITULO, BRANCO, TELA, LARGURA // 2, ALTURA // 4 - 50)
        for i, opcao in enumerate(opcoes_menu):
            cor = AMARELO if i == opcao_selecionada else BRANCO
            desenhar_texto(opcao, FONTE, cor, TELA, LARGURA // 2, ALTURA // 2 + i * 60 - 20)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: rodando = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    som_navegacao_menu.play()
                    if event.key == pygame.K_UP: opcao_selecionada = (opcao_selecionada - 1) % len(opcoes_menu)
                    else: opcao_selecionada = (opcao_selecionada + 1) % len(opcoes_menu)
                elif event.key == pygame.K_RETURN:
                    som_selecao_menu.play()
                    opcao_escolhida = opcoes_menu[opcao_selecionada]
                    if opcao_escolhida == "Iniciar Jogo":
                        modo_quase_impossivel = False
                        nivel = 1
                        iniciar_nivel()
                        estado_jogo = "jogando"
                    elif opcao_escolhida == "Quase Impossível":
                        modo_quase_impossivel = True
                        iniciar_nivel()
                        estado_jogo = "jogando"
                    elif opcao_escolhida == "Regras": estado_jogo = "regras"
                    elif opcao_escolhida == "Sobre": estado_jogo = "sobre"
                    elif opcao_escolhida == "Recordes":
                        # Inicia na aba "comum" se houver recordes, senão na "impossivel"
                        aba_recordes = 'comum' if high_scores.get('comum') else 'impossivel'
                        estado_jogo = "recordes"
                    elif opcao_escolhida == "Sair": rodando = False

    # Tela de regras com a mecânica de score
    elif estado_jogo == "regras":
        TELA.fill(PRETO)
        desenhar_texto("Regras", FONTE_TITULO, BRANCO, TELA, LARGURA // 2, 100)
        desenhar_texto("- Quanto mais rápido você clica, mais pontos ganha!", FONTE_PEQUENA, AMARELO, TELA, 100, 200, "topo_esquerda")
        desenhar_texto("- Acertos em sequência aumentam seu COMBO.", FONTE_PEQUENA, BRANCO, TELA, 100, 250, "topo_esquerda")
        desenhar_texto("- A pontuação final é multiplicada pelo combo.", FONTE_PEQUENA, BRANCO, TELA, 100, 300, "topo_esquerda")
        desenhar_texto("- Errar um clique ou acertar um alvo azul ZERA o combo.", FONTE_PEQUENA, BRANCO, TELA, 100, 350, "topo_esquerda")
        desenhar_texto("- O modo 'Quase Impossível' não permite erros.", FONTE_PEQUENA, VERMELHO, TELA, 100, 400, "topo_esquerda")
        desenhar_texto("Pressione ESC para voltar ao menu", FONTE, AMARELO, TELA, LARGURA // 2, ALTURA - 50)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: rodando = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                som_selecao_menu.play()
                estado_jogo = "menu_inicial"
    
    # Tela de sobre com informações do desenvolvimento
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
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                som_selecao_menu.play()
                estado_jogo = "menu_inicial"

    elif estado_jogo == "recordes":
        TELA.fill(PRETO)

        # Abas de recorde
        cor_comum = AMARELO if aba_recordes == 'comum' else BRANCO
        cor_impossivel = AMARELO if aba_recordes == 'impossivel' else BRANCO
        desenhar_texto("Recordes Comuns", FONTE_PEQUENA, cor_comum, TELA, LARGURA // 4, 100)
        desenhar_texto("Recordes Impossíveis", FONTE_PEQUENA, cor_impossivel, TELA, LARGURA * 3 // 4, 100)

        lista_atual = high_scores.get(aba_recordes, [])

        if not confirmando_reset:
            if not lista_atual:
                desenhar_texto("Nenhum recorde salvo ainda!", FONTE, BRANCO, TELA, LARGURA // 2, ALTURA // 2)
            else:
                for i, (nome, score) in enumerate(lista_atual):
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
                    som_selecao_menu.play()
                    confirmando_reset = False
                    estado_jogo = "menu_inicial"
                if not confirmando_reset:
                    if event.key == pygame.K_r:
                        som_navegacao_menu.play()
                        confirmando_reset = True
                    elif event.key == pygame.K_RIGHT:
                        som_navegacao_menu.play()
                        aba_recordes = 'impossivel'
                    elif event.key == pygame.K_LEFT:
                        som_navegacao_menu.play()
                        aba_recordes = 'comum'
                else:
                    if event.key == pygame.K_s:
                        som_acerto_penalidade.play()
                        high_scores[aba_recordes] = []
                        salvar_high_scores(high_scores)
                        confirmando_reset = False
                    elif event.key == pygame.K_n:
                        som_selecao_menu.play()
                        confirmando_reset = False

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
                    som_selecao_menu.play()
                    modo_salvar = 'impossivel' if modo_quase_impossivel else 'comum'
                    high_scores = adicionar_high_score(nome_jogador, pontos_finais_para_salvar, high_scores, modo_salvar)
                    salvar_high_scores(high_scores)
                    estado_jogo = "recordes"
                elif event.key == pygame.K_BACKSPACE:
                    nome_jogador = nome_jogador[:-1]
                    som_navegacao_menu.play()
                elif len(nome_jogador) < 6 and event.unicode.isalnum():
                    nome_jogador += event.unicode
                    som_navegacao_menu.play()

    elif estado_jogo == "transicao_nivel":
        TELA.fill(PRETO)
        desenhar_texto(f"Nível {nivel + 1}", FONTE_TITULO, BRANCO, TELA, LARGURA // 2, ALTURA // 3)
        desenhar_texto(f"Meta: {METAS[nivel + 1]} pontos", FONTE, BRANCO, TELA, LARGURA // 2, ALTURA // 2)
        desenhar_texto("Pressione ESPAÇO para continuar", FONTE, AMARELO, TELA, LARGURA // 2, ALTURA * 2 // 3)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: rodando = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                som_level_up.play()
                nivel += 1
                iniciar_nivel()
                estado_jogo = "jogando"

    elif estado_jogo == "jogando":
        # --- 6. CUIDANDO DOS INPUTS DO JOGADOR ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT: rodando = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                tempo_do_clique = pygame.time.get_ticks() # Captura o tempo exato do clique
                pos_mouse = pygame.mouse.get_pos()
                acertou_alvo = False
                for alvo_dict in alvos[:]:
                    if alvo_dict['rect'].collidepoint(pos_mouse):
                        acertou_alvo = True
                        tipo_alvo = alvo_dict['tipo']
                        
                        # A lógica de pontuação baseada no tempo
                        if tipo_alvo == 'normal' or tipo_alvo == 'bonus':
                            combo_atual += 1
                            
                            # Calcula a "idade" (tempo aparecendo) do alvo em milissegundos
                            tempo_de_vida_alvo = tempo_do_clique - alvo_dict['tempo_criacao']
                            
                            # Fórmula: 100 pontos base, perdendo 40 pontos por segundo de vida do alvo
                            pontos_base = max(10, 100 - (tempo_de_vida_alvo / 1000) * 40)
                            
                            if tipo_alvo == 'bonus':
                                som_acerto_bonus.play()
                                pontos_base *= 3 # Bônus triplica os pontos base
                            else:
                                som_acerto_normal.play()
                            
                            pontos += int(pontos_base * combo_atual)

                        elif tipo_alvo == 'penalidade':
                            som_acerto_penalidade.play()
                            combo_atual = 0
                            pontos -= 100 # Penalidade severa se errar
                            
                            if modo_quase_impossivel:
                                som_game_over.play()
                                pontos_finais_para_salvar = pontos
                                
                                if len(high_scores['impossivel']) < 5 or pontos_finais_para_salvar > (high_scores['impossivel'][-1][1] if high_scores['impossivel'] else 0):
                                    estado_jogo = "inserir_nome"
                                else:
                                    estado_jogo = "game_over"

                        pontos = max(0, pontos) # Garante que a pontuação não seja negativa
                        alvos.remove(alvo_dict)
                        break
                
                if not acertou_alvo:
                    som_erro_clique.play()
                    combo_atual = 0
                    if modo_quase_impossivel:
                        som_game_over.play()
                        pontos_finais_para_salvar = pontos
                        if len(high_scores['impossivel']) < 5 or pontos_finais_para_salvar > (high_scores['impossivel'][-1][1] if high_scores['impossivel'] else 0):
                            estado_jogo = "inserir_nome"
                        else:
                            estado_jogo = "game_over"

        # --- 7. A LÓGICA ---
        tempo_agora = pygame.time.get_ticks()
        
        
        if modo_quase_impossivel:
            if tempo_agora - tempo_inicio > tempo_aumento_dificuldade:
                TEMPO_PARA_SPAWN = max(100, TEMPO_PARA_SPAWN - DIFICULDADES['quase_impossivel']['velocidade_aumento'])
                tempo_aumento_dificuldade += 10000

        # Remove alvos que não foram clicados no modo impossível
        if modo_quase_impossivel:
            alvos_a_remover = [alvo for alvo in alvos if tempo_agora - alvo['tempo_criacao'] > 2000]
            for alvo in alvos_a_remover:
                alvos.remove(alvo)

        # Lógica do alvo
        if tempo_agora - ultimo_spawn > TEMPO_PARA_SPAWN:
            raio_alvo = random.randint(raio_min, raio_max)
            pos_x = random.randint(raio_alvo, LARGURA - raio_alvo)
            pos_y = random.randint(raio_alvo, ALTURA - raio_alvo)
            rect = pygame.Rect(pos_x - raio_alvo, pos_y - raio_alvo, raio_alvo * 2, raio_alvo * 2)
            chance = random.random()
            if chance < 0.7: tipo, cor = 'normal', VERMELHO
            elif chance < 0.85: tipo, cor = 'bonus', VERDE
            else: tipo, cor = 'penalidade', AZUL
           
            novo_alvo = {'rect': rect, 'tipo': tipo, 'cor': cor, 'tempo_criacao': tempo_agora}
            alvos.append(novo_alvo)
            ultimo_spawn = tempo_agora
        
        # Lógica do temporizador
        tempo_decorrido = tempo_agora - tempo_inicio
        tempo_restante = (TEMPO_DO_NIVEL - tempo_decorrido) // 1000 # Converte para segundos
        if tempo_restante < 0: tempo_restante = 0

        # Verifica se a meta do nível foi atingida ou se o tempo acabou
        if not modo_quase_impossivel:
            if pontos >= METAS[nivel]:
                if nivel < 3:
                    estado_jogo = "transicao_nivel"
                else:
                    som_vitoria.play()
                    pontos_base_final = pontos
                    bonus_tempo_final = tempo_restante * 20
                    pontos_finais_para_salvar = pontos + bonus_tempo_final
                    if len(high_scores['comum']) < 5 or pontos_finais_para_salvar > (high_scores['comum'][-1][1] if high_scores['comum'] else 0):
                        estado_jogo = "inserir_nome"
                    else:
                        estado_jogo = "vitoria"
            elif tempo_decorrido >= TEMPO_DO_NIVEL:
                som_game_over.play()
                pontos_finais_para_salvar = pontos
                if len(high_scores['comum']) < 5 or pontos_finais_para_salvar > (high_scores['comum'][-1][1] if high_scores['comum'] else 0):
                    estado_jogo = "inserir_nome"
                else:
                    estado_jogo = "game_over"

        # --- 8. DESENHANDO NA TELA ---
        TELA.fill(PRETO)
        # Desenha um círculo para cada alvo 
        for alvo_dict in alvos: pygame.draw.circle(TELA, alvo_dict['cor'], alvo_dict['rect'].center, alvo_dict['rect'].width // 2)
        # Desenha o placar de pontos
        texto_pontos_surface = FONTE.render(f"Pontos: {pontos}", True, BRANCO)
        TELA.blit(texto_pontos_surface, (10, 10))
        
        if not modo_quase_impossivel:
            texto_meta_surface = FONTE.render(f"/ {METAS[nivel]}", True, BRANCO)
            TELA.blit(texto_meta_surface, (texto_pontos_surface.get_width() + 15, 10))
            # Desenha o temporizador
            texto_tempo_surface = FONTE.render(f"Tempo: {tempo_restante}", True, BRANCO)
            pos_x_tempo = LARGURA - texto_tempo_surface.get_width() - 10
            TELA.blit(texto_tempo_surface, (pos_x_tempo, 10))
            
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
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                som_selecao_menu.play()
                estado_jogo = "menu_inicial"
    # Gerencia a tela de Game Over
    elif estado_jogo == "game_over":
        TELA.fill(PRETO)
        desenhar_texto("GAME OVER", FONTE_TITULO, VERMELHO, TELA, LARGURA // 2, ALTURA // 3)
        desenhar_texto(f"Sua pontuação: {pontos}", FONTE, BRANCO, TELA, LARGURA // 2, ALTURA // 2)
        
        modo_atual = 'impossivel' if modo_quase_impossivel else 'comum'
        recordes_do_modo = high_scores.get(modo_atual, [])
        recorde_maximo = recordes_do_modo[0][1] if recordes_do_modo else 0
        desenhar_texto(f"Recorde: {recorde_maximo}", FONTE, AMARELO, TELA, LARGURA // 2, ALTURA // 2 + 50)
        desenhar_texto("Pressione ESPAÇO para tentar novamente", FONTE_PEQUENA, BRANCO, TELA, LARGURA // 2, ALTURA * 5 // 6)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: rodando = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                som_selecao_menu.play()
                estado_jogo = "menu_inicial"

    pygame.display.flip()

# --- 9. TUDO ACABOU ---
pygame.quit()