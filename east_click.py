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
AZUL = (0, 100, 255) #Cor para alvos de penalidade

# Para controlar a velocidade do jogo
relogio = pygame.time.Clock()
FPS = 60

# Configuração da fonte para exibir texto na tela
FONTE_TITULO = pygame.font.Font(None, 74) 
FONTE = pygame.font.Font(None, 50)  

# --- FUNÇÕES AUXILIARES ---
def desenhar_texto(texto, fonte, cor, superficie, x, y):
    textobj = fonte.render(texto, True, cor)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    superficie.blit(textobj, textrect)

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

# --- 2. VARIÁVEIS DO JOGO ---
estado_jogo = "menu_inicial" 
nivel = 1
METAS = {1: 15, 2: 25} 
DIFICULDADES = {
    1: {'spawn': 1000, 'raio_min': 30, 'raio_max': 60}, 
    2: {'spawn': 750, 'raio_min': 20, 'raio_max': 45}   
}
alvos = []
TEMPO_PARA_SPAWN = None
ultimo_spawn = 0
raio_min, raio_max = 0, 0
pontos = 0
TEMPO_DO_NIVEL = 30000 
tempo_inicio = 0

# --- 3. O CORAÇÃO DO JOGO (LOOP PRINCIPAL) ---
rodando = True
while rodando:
    relogio.tick(FPS)

    if estado_jogo == "menu_inicial":
       
        TELA.fill(PRETO)
        desenhar_texto("Alvo Rápido", FONTE_TITULO, BRANCO, TELA, LARGURA // 2, ALTURA // 4)
        desenhar_texto("Pressione ESPAÇO para começar", FONTE, BRANCO, TELA, LARGURA // 2, ALTURA // 2)
        desenhar_texto("Acerte a meta de pontos antes do tempo acabar!", FONTE, BRANCO, TELA, LARGURA // 2, ALTURA * 3 // 4)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rodando = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                nivel = 1
                iniciar_nivel()
                estado_jogo = "jogando"

    elif estado_jogo == "jogando":
        # --- 4. CUIDANDO DOS INPUTS DO JOGADOR ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rodando = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos_mouse = pygame.mouse.get_pos()
                
                #  Itera sobre a lista de dicionários de alvos
                for alvo_dict in alvos[:]:
                    if alvo_dict['rect'].collidepoint(pos_mouse):
                        tipo_alvo = alvo_dict['tipo']
                        
                        #  Aplica o efeito com base no tipo do alvo
                        if tipo_alvo == 'normal':
                            pontos += 1
                        elif tipo_alvo == 'bonus':
                            pontos += 5 # Bônus vale mais!
                        elif tipo_alvo == 'penalidade':
                            pontos -= 3 # Penalidade tira pontos
                        
                        # Garante que os pontos não fiquem negativos
                        pontos = max(0, pontos)
                        
                        alvos.remove(alvo_dict)

        # --- 5. A LÓGICA ---
        tempo_agora = pygame.time.get_ticks()
        
        #  Lógica de spawn agora sorteia o tipo de alvo
        if tempo_agora - ultimo_spawn > TEMPO_PARA_SPAWN:
            raio_alvo = random.randint(raio_min, raio_max)
            pos_x = random.randint(raio_alvo, LARGURA - raio_alvo)
            pos_y = random.randint(raio_alvo, ALTURA - raio_alvo)
            rect = pygame.Rect(pos_x - raio_alvo, pos_y - raio_alvo, raio_alvo * 2, raio_alvo * 2)
            
            #  Sorteia o tipo do alvo com base em probabilidades
            chance = random.random() # Sorteia um número entre 0.0 e 1.0
            if chance < 0.7: # 70% de chance de ser normal
                tipo = 'normal'
                cor = VERMELHO
            elif chance < 0.85: # 15% de chance de ser bônus
                tipo = 'bonus'
                cor = VERDE
            else: # 15% de chance de ser penalidade
                tipo = 'penalidade'
                cor = AZUL
            
            # _NOVO_: Cria o dicionário do alvo e adiciona na lista
            novo_alvo = {'rect': rect, 'tipo': tipo, 'cor': cor}
            alvos.append(novo_alvo)
            
            ultimo_spawn = tempo_agora
        
        # Lógica do temporizador 
        tempo_decorrido = tempo_agora - tempo_inicio
        tempo_restante = (TEMPO_DO_NIVEL - tempo_decorrido) // 1000
        if tempo_restante < 0:
            tempo_restante = 0

        # Lógica de vitória e game over 
        if pontos >= METAS[nivel]:
            if nivel == 1: 
                nivel = 2
                iniciar_nivel()
            else: 
                estado_jogo = "vitoria"
        elif tempo_decorrido >= TEMPO_DO_NIVEL: 
            estado_jogo = "game_over"

        # --- 6. DESENHANDO NA TELA ---
        TELA.fill(PRETO)

        # Desenha cada alvo usando as informações do seu dicionário
        for alvo_dict in alvos:
            pygame.draw.circle(TELA, alvo_dict['cor'], alvo_dict['rect'].center, alvo_dict['rect'].width // 2)
        
        texto_pontos_surface = FONTE.render(f"Pontos: {pontos} / {METAS[nivel]}", True, BRANCO)
        TELA.blit(texto_pontos_surface, (10, 10))
        
        texto_tempo_surface = FONTE.render(f"Tempo: {tempo_restante}", True, BRANCO)
        pos_x_tempo = LARGURA - texto_tempo_surface.get_width() - 10
        TELA.blit(texto_tempo_surface, (pos_x_tempo, 10))

    # Seções "vitoria" e "game_over" 
    elif estado_jogo == "vitoria":
        TELA.fill(PRETO)
        desenhar_texto("VOCÊ VENCEU!", FONTE_TITULO, VERDE, TELA, LARGURA // 2, ALTURA // 3)
        desenhar_texto(f"Pontuação Final: {pontos}", FONTE, BRANCO, TELA, LARGURA // 2, ALTURA // 2)
        desenhar_texto("Pressione ESPAÇO para jogar de novo", FONTE, BRANCO, TELA, LARGURA // 2, ALTURA * 2 // 3)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rodando = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                estado_jogo = "menu_inicial"

    elif estado_jogo == "game_over":
        TELA.fill(PRETO)
        desenhar_texto("GAME OVER", FONTE_TITULO, VERMELHO, TELA, LARGURA // 2, ALTURA // 3)
        desenhar_texto(f"Sua pontuação: {pontos}", FONTE, BRANCO, TELA, LARGURA // 2, ALTURA // 2)
        desenhar_texto("Pressione ESPAÇO para tentar novamente", FONTE, BRANCO, TELA, LARGURA // 2, ALTURA * 2 // 3)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rodando = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                estado_jogo = "menu_inicial"

    pygame.display.flip()

# --- 7. TUDO ACABOU ---
pygame.quit()