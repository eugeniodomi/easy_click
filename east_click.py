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

# Para controlar a velocidade do jogo
relogio = pygame.time.Clock()
FPS = 60

# Configuração da fonte para exibir texto na tela
FONTE = pygame.font.Font(None, 50)  

# --- 2. VARIÁVEIS DO JOGO ---

# Alvos que aparecem na tela
alvos = []

# Lógica de "spawn" dos alvos
TEMPO_PARA_SPAWN = 1000  # 1 segundo
ultimo_spawn = pygame.time.get_ticks()  # Guarda o tempo do último alvo criado

# Pontuação
pontos = 0

#Variáveis para o temporizador do nível
TEMPO_DO_NIVEL = 30000 # 30 segundos em milissegundos
tempo_inicio = pygame.time.get_ticks() # Registra quando o jogo começou

# --- 3. O CORAÇÃO DO JOGO (LOOP PRINCIPAL) ---
rodando = True
while rodando:
    relogio.tick(FPS)

    # --- 4. CUIDANDO DOS INPUTS DO JOGADOR ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            rodando = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos_mouse = pygame.mouse.get_pos()
 
            for alvo in alvos[:]:
                if alvo.collidepoint(pos_mouse):
                    pontos += 1
                    alvos.remove(alvo)
                    # print(f"Acertou! Pontuação: {pontos}") 

    # --- 5. A LÓGICA ---

    # Lógica do novo alvo 
    tempo_agora = pygame.time.get_ticks()
    if tempo_agora - ultimo_spawn > TEMPO_PARA_SPAWN:
        raio_alvo = random.randint(20, 50)
        pos_x = random.randint(raio_alvo, LARGURA - raio_alvo)
        pos_y = random.randint(raio_alvo, ALTURA - raio_alvo)
        novo_alvo = pygame.Rect(pos_x - raio_alvo, pos_y - raio_alvo, raio_alvo * 2, raio_alvo * 2)
        alvos.append(novo_alvo)
        ultimo_spawn = tempo_agora
        
    # Lógica do temporizador
    tempo_decorrido = tempo_agora - tempo_inicio
    tempo_restante = (TEMPO_DO_NIVEL - tempo_decorrido) // 1000 # Converte para segundos
    
    # Garante que o tempo não fique negativo na tela
    if tempo_restante < 0:
        tempo_restante = 0

    # Verifica se o tempo acabou para encerrar o jogo
    if tempo_decorrido >= TEMPO_DO_NIVEL:
        rodando = False

    # --- 6. DESENHANDO NA TELA ---
    TELA.fill(PRETO)

    # Desenha um círculo para cada alvo na nossa lista
    for alvo in alvos:
        pygame.draw.circle(TELA, VERMELHO, alvo.center, alvo.width // 2)

    # _NOVO_: Desenhar o placar de pontos
    texto_pontos_surface = FONTE.render(f"Pontos: {pontos}", True, BRANCO)
    TELA.blit(texto_pontos_surface, (10, 10)) # Posição (x, y) no canto superior esquerdo

    # _NOVO_: Desenhar o temporizador
    texto_tempo_surface = FONTE.render(f"Tempo: {tempo_restante}", True, BRANCO)
    # Posiciona o texto no canto superior direito
    pos_x_tempo = LARGURA - texto_tempo_surface.get_width() - 10
    TELA.blit(texto_tempo_surface, (pos_x_tempo, 10))

    pygame.display.flip()

# --- 7. TUDO ACABOU ---
# _NOVO_: Feedback final no terminal
print(f"Fim de Jogo! Pontuação Final: {pontos}")
pygame.quit()