import json
import os
import uuid
import tornado.ioloop
import tornado.web
import tornado.websocket

from game_manager import game_state, init_game

# Armazena jogadores conectados
clients = {}

# Envia o estado do jogo para todos os jogadores
def broadcast():
    msg = json.dumps(game_state)
    for client in clients.values():
        client.write_message(msg)

# Classe principal do WebSocket (tempo real)
class GameWebSocket(tornado.websocket.WebSocketHandler):

    # Quando um jogador conecta
    def open(self):
        print("Novo jogador conectou!")

        # Limita a 2 jogadores
        if len(clients) >= 2:
            self.write_message(json.dumps({"error": "Sala cheia"}))
            self.close()
            return

        # Gera ID único
        player_id = str(uuid.uuid4())[:5]
        self.player_id = player_id

        clients[player_id] = self
        game_state["players"].append(player_id)

        # Define quem começa
        if game_state["current_player"] is None:
            game_state["current_player"] = player_id

        # Envia estado inicial
        self.write_message(json.dumps({
            "state": game_state,
            "player_id": player_id
        }))

        broadcast()

    # Quando jogador faz uma ação
    def on_message(self, message):
        data = json.loads(message)

        # Reiniciar jogo
        if data.get("action") == "restart":
            init_game()

            if game_state["players"]:
                game_state["current_player"] = game_state["players"][0]

            game_state["winner"] = None
            broadcast()
            return

        r, c = data["r"], data["c"]

        # Regras básicas
        if game_state["game_over"]:
            return

        if self.player_id != game_state["current_player"]:
            return  # impede jogar fora do turno

        if game_state["revealed"][r][c]:
            return

        # Marca célula como revelada
        game_state["revealed"][r][c] = True

        # Se for bomba → jogador perde
        if game_state["board"][r][c] == 1:
            game_state["game_over"] = True

            # Define outro jogador como vencedor
            for p in game_state["players"]:
                if p != self.player_id:
                    game_state["winner"] = p

        else:
            # Troca turno entre os 2 jogadores
            players = game_state["players"]
            if len(players) == 2:
                idx = players.index(self.player_id)
                game_state["current_player"] = players[(idx + 1) % 2]

        broadcast()

    # Quando jogador desconecta
    def on_close(self):
        pid = self.player_id
        clients.pop(pid, None)

        if pid in game_state["players"]:
            game_state["players"].remove(pid)

        print(f"Jogador {pid} desconectado")

    def check_origin(self, origin):
        return True  # permite conexões externas (ngrok)

# Caminho base do projeto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Configuração do servidor
def make_app():
    return tornado.web.Application([
        (r"/ws", GameWebSocket),  # rota do WebSocket
        (r"/(.*)", tornado.web.StaticFileHandler, {
            "path": os.path.join(BASE_DIR, "..", "client"),
            "default_filename": "index.html"
        }),
    ])

# Inicialização
if __name__ == "__main__":
    init_game()

    app = make_app()
    app.listen(8000)

    print("Servidor rodando em http://localhost:8000")

    tornado.ioloop.IOLoop.current().start()