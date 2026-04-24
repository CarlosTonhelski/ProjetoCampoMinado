import random

game_state = {
    "board": [],
    "revealed": [],
    "game_over": False,
    "current_player": None,
    "players": [],
    "winner": None
}

def init_game(size=5):
    game_state["board"] = [[0]*size for _ in range(size)]
    game_state["revealed"] = [[False]*size for _ in range(size)]
    game_state["game_over"] = False
    game_state["winner"] = None
    game_state["current_player"] = None

    r = random.randint(0, size-1)
    c = random.randint(0, size-1)
    game_state["board"][r][c] = 1