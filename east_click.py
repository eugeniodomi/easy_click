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

# --- 2. VARIÁVEIS DO JOGO ---

# Alvos que aparecem na tela
alvos = []

# Lógica de "spawn" dos alvos
TEMPO_PARA_SPAWN = 1000  # 1 segundo
ultimo_spawn = pygame.time.get_ticks()  # Guarda o tempo do último alvo criado

# Pontuação
pontos = 0

# --- 3. O CORAÇÃO DO JOGO (LOOP PRINCIPAL) ---
rodando = True
while rodando:
    relogio.tick(FPS)

    # --- 4. CUIDANDO DOS INPUTS DO JOGADOR ---
    for event in pygame.event.get():
        # Se o jogador clicar no 'X' da janela, o jogo fecha
        if event.type == pygame.QUIT:
            rodando = False

        # Checando se o mouse foi clicado
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos_mouse = pygame.mouse.get_pos()

            # Iterar sobre uma cópia para poder remover itens da lista 
            for alvo in alvos[:]:
                # Checa se a coordenada do clique está dentro do alvo
                if alvo.collidepoint(pos_mouse):
                    pontos += 1
                    alvos.remove(alvo)
                    print(f"Acertou! Pontuação: {pontos}") 

    # --- 5. A LÓGICA

    # Novo alvo
    tempo_agora = pygame.time.get_ticks()
    if tempo_agora - ultimo_spawn > TEMPO_PARA_SPAWN:
        # Tamanho aleatório para o alvo
        raio_alvo = random.randint(20, 50)
        
        # Posição aleatória, mas garantindo que o círculo fique 100% dentro da tela
        pos_x = random.randint(raio_alvo, LARGURA - raio_alvo)
        pos_y = random.randint(raio_alvo, ALTURA - raio_alvo)

        # Pygame usa para representar o alvo
        novo_alvo = pygame.Rect(pos_x - raio_alvo, pos_y - raio_alvo, raio_alvo * 2, raio_alvo * 2)
        alvos.append(novo_alvo)

        # Reseta o contador para o próximo spawn
        ultimo_spawn = tempo_agora

    # --- 6. DESENHANDO NA TELA ---

    # Pinta o fundo de preto
    TELA.fill(PRETO)

    # Desenha um círculo para cada alvo na nossa lista
    for alvo in alvos:
        # O círculo é desenhado usando as informações do "retângulo"
        pygame.draw.circle(TELA, VERMELHO, alvo.center, alvo.width // 2)

    # Mostra tudo 
    pygame.display.flip()

# --- 7. TUDO ACABOU ---
pygame.quit()