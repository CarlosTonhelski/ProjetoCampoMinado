import json
import os
import uuid
import tornado.ioloop
import tornado.web
import tornado.websocket

from game_manager import game_state, init_game

clients = {}

def broadcast():
    msg = json.dumps(game_state)
    for client in clients.values():
        client.write_message(msg)

class GameWebSocket(tornado.websocket.WebSocketHandler):

    def open(self):
        print("Novo jogador conectou!")

        if len(clients) >= 2:
            self.write_message(json.dumps({"error": "Sala cheia"}))
            self.close()
            return

        player_id = str(uuid.uuid4())[:5]
        self.player_id = player_id

        clients[player_id] = self
        game_state["players"].append(player_id)

        if game_state["current_player"] is None:
            game_state["current_player"] = player_id

        self.write_message(json.dumps({
            "state": game_state,
            "player_id": player_id
        }))

        broadcast()

    def on_message(self, message):
        data = json.loads(message)

        # Restart
        if data.get("action") == "restart":
            init_game()

            if game_state["players"]:
                game_state["current_player"] = game_state["players"][0]

            game_state["winner"] = None
            broadcast()
            return

        r, c = data["r"], data["c"]

        if game_state["game_over"]:
            return

        if self.player_id != game_state["current_player"]:
            return

        if game_state["revealed"][r][c]:
            return

        game_state["revealed"][r][c] = True

        # BOMBA → QUEM CLICA PERDE
        if game_state["board"][r][c] == 1:
            game_state["game_over"] = True

            for p in game_state["players"]:
                if p != self.player_id:
                    game_state["winner"] = p

        else:
            players = game_state["players"]
            if len(players) == 2:
                idx = players.index(self.player_id)
                game_state["current_player"] = players[(idx + 1) % 2]

        broadcast()

    def on_close(self):
        pid = self.player_id
        clients.pop(pid, None)

        if pid in game_state["players"]:
            game_state["players"].remove(pid)

        print(f"Jogador {pid} desconectado")

    def check_origin(self, origin):
        return True


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def make_app():
    return tornado.web.Application([
        (r"/ws", GameWebSocket),
        (r"/(.*)", tornado.web.StaticFileHandler, {
            "path": os.path.join(BASE_DIR, "..", "client"),
            "default_filename": "index.html"
        }),
    ])

if __name__ == "__main__":
    init_game()

    app = make_app()
    app.listen(8000)

    print("Servidor rodando em http://localhost:8000")

    tornado.ioloop.IOLoop.current().start()