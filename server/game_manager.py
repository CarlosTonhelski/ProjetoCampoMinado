import random

# Estado global do jogo (compartilhado entre todos os jogadores)
game_state = {
    "board": [],           # Tabuleiro (0 = seguro, 1 = bomba)
    "revealed": [],        # Quais células já foram clicadas
    "game_over": False,    # Indica se o jogo terminou
    "current_player": None,# Jogador da vez
    "players": [],         # Lista de jogadores conectados
    "winner": None         # Quem venceu
}

def init_game(size=5): # Cria tabuleiro, define as células e sorteia a bomba
    # Cria matriz 5x5 com zeros
    game_state["board"] = [[0]*size for _ in range(size)]

    # Nenhuma célula revelada
    game_state["revealed"] = [[False]*size for _ in range(size)]

    game_state["game_over"] = False
    game_state["winner"] = None
    game_state["current_player"] = None  # Reinicia turno

    # Sorteia uma bomba em posição aleatória
    r = random.randint(0, size-1)
    c = random.randint(0, size-1)
    game_state["board"][r][c] = 1