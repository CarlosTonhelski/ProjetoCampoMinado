import asyncio
import websockets
import json
import random
import uuid

# Estado Global
game_state = {
    "board": [],
    "revealed": [],
    "game_over": False,
    "last_player": None,
    "players": set(),          # jogadores conectados
    "players_played": set()    # quem já jogou na rodada
}

def init_game(size=5, bombs=3):
    game_state["board"] = [[0 for _ in range(size)] for _ in range(size)]
    game_state["revealed"] = [[False for _ in range(size)] for _ in range(size)]
    game_state["game_over"] = False
    game_state["last_player"] = None
    game_state["players_played"] = set()

    count = 0
    while count < bombs:
        r, c = random.randint(0, size-1), random.randint(0, size-1)
        if game_state["board"][r][c] == 0:
            game_state["board"][r][c] = 1
            count += 1

clients = {}

async def broadcast_state():
    if clients:
        state_copy = dict(game_state)
        state_copy["players"] = list(game_state["players"])
        state_copy["players_played"] = list(game_state["players_played"])

        message = json.dumps(state_copy)

        await asyncio.gather(
            *[ws.send(message) for ws in clients.values()],
            return_exceptions=True
        )

async def handler(websocket):
    player_id = str(uuid.uuid4())[:8]
    clients[player_id] = websocket
    game_state["players"].add(player_id)

    print(f"Jogador {player_id} conectado! Total: {len(clients)}")

    try:
        await broadcast_state()

        async for message in websocket:
            data = json.loads(message)
            r, c = data.get('r'), data.get('c')

            if r is None or c is None:
                continue

            if not (0 <= r < len(game_state["board"]) and 0 <= c < len(game_state["board"])):
                continue

            # 🚫 já jogou na rodada
            if player_id in game_state["players_played"]:
                print(f"{player_id} já jogou nesta rodada")
                continue

            # 💥 game over → reinicia
            if game_state["game_over"]:
                init_game()
                await broadcast_state()
                continue

            print(f"{player_id} jogou em {r},{c}")
            game_state["last_player"] = player_id
            game_state["players_played"].add(player_id)

            if game_state["board"][r][c] == 1:
                game_state["game_over"] = True
            else:
                game_state["revealed"][r][c] = True

            # 🔁 se todos jogaram → nova rodada
            if game_state["players_played"] == game_state["players"]:
                print("Nova rodada!")
                game_state["players_played"] = set()

            await broadcast_state()

    except websockets.exceptions.ConnectionClosed:
        pass

    finally:
        del clients[player_id]
        game_state["players"].discard(player_id)
        game_state["players_played"].discard(player_id)

        print(f"Jogador {player_id} desconectado.")
        await broadcast_state()

async def main():
    init_game()
    print("Servidor iniciado na porta 8765")

    async with websockets.serve(handler, "0.0.0.0", 8765):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())