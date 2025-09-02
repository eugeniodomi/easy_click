# easy_click

## Alvo Rápido

Um jogo de arcade e precisão desenvolvido em Python com a biblioteca Pygame. O objetivo é testar os reflexos e a velocidade do jogador ao clicar em alvos que aparecem na tela, buscando a maior pontuação possível em um sistema de jogo com múltiplos níveis e combos.

Este projeto foi desenvolvido por Eugenio Domingues como trabalho para a disciplina de Linguagem de Programação Aplicada do centro universitário Uninter.

![Captura de Tela do Jogo](placeholder.png)
*(Você pode substituir esta imagem por uma captura de tela do seu jogo)*

---

## Funcionalidades (Features)

O jogo foi desenvolvido com uma estrutura robusta e conta com diversas funcionalidades para criar uma experiência completa:

-   **Três Níveis de Dificuldade Progressiva:** O jogo possui 3 níveis, cada um aumentando a velocidade de surgimento dos alvos e diminuindo seu tamanho.
-   **Sistema de Pontuação Dinâmico:** A pontuação não é fixa! Quanto mais rápido o jogador clica em um alvo após ele aparecer, mais pontos base ele ganha.
-   **Mecânica de Combo:** Acertos consecutivos aumentam um multiplicador de combo, que potencializa drasticamente a pontuação. Errar um clique ou acertar um alvo de penalidade quebra o combo.
-   **Variedade de Alvos:**
    -   **Alvo Normal (Vermelho):** Concede pontos base.
    -   **Alvo Bônus (Verde):** Multiplica os pontos base do acerto.
    -   **Alvo de Penalidade (Azul):** Zera o combo e subtrai pontos.
-   **Bônus por Tempo:** Ao concluir o último nível, os segundos restantes são convertidos em um bônus de pontos, recompensando a agilidade.
-   **Ranking de High Scores:** O jogo salva um Top 5 dos melhores recordes em um arquivo `highscores.json`, registrando o nome (6 caracteres) e a pontuação dos jogadores.
-   **Menu Navegável Completo:** Um menu inicial completo com opções para:
    -   Iniciar o Jogo
    -   Ver as Regras
    -   Tela Sobre
    -   Visualizar o Ranking de Recordes (com opção de reset)
    -   Sair do Jogo
-   **Efeitos Sonoros e Música:** O jogo conta com música de fundo em loop e efeitos sonoros para navegação no menu, acertos, erros e transições de estado, tornando a experiência mais imersiva.

---

## Tecnologias Utilizadas

-   **Python 3**
-   **Pygame** (biblioteca para desenvolvimento de jogos)

---

## Pré-requisitos

Antes de executar, certifique-se de ter o seguinte instalado:

-   **Python 3:** [python.org](https://www.python.org/)
-   **Pygame:** Pode ser instalado via `pip`.
    ```bash
    pip install pygame
    ```

---

## Como Executar

1.  Clone ou baixe este repositório para a sua máquina local.
2.  Certifique-se de que o arquivo principal (`.py`), o arquivo `highscores.json` (será criado na primeira vez que jogar) e a pasta `sons` estejam no mesmo diretório.
3.  Navegue até o diretório do projeto pelo seu terminal ou prompt de comando.
4.  Execute o seguinte comando (substitua `nome_do_arquivo.py` pelo nome real do seu script):
    ```bash
    python nome_do_arquivo.py
    ```

---

## Como Jogar

-   **Objetivo:** Atingir a meta de pontos em cada um dos três níveis antes que o tempo de 40 segundos se esgote.

-   **Controles:**
    -   **Menu:** Use as **Setas (CIMA/BAIXO)** para navegar e **ENTER** para selecionar.
    -   **Jogo:** Use o **MOUSE** para mirar e o **BOTÃO ESQUERDO** para clicar nos alvos.

-   **Gameplay:**
    -   Seja rápido! A pontuação de cada alvo diminui a cada instante que ele permanece na tela.
    -   Mantenha a precisão para construir combos e multiplicar sua pontuação.
    -   Priorize os alvos verdes (bônus) e, acima de tudo, evite os alvos azuis (penalidade).