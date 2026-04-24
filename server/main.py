import json
import os
import uuid
import tornado.ioloop
import tornado.web
import tornado.websocket

from server.game_manager import game_state, init_game

clients = {} # Dicionário para armazenar os clientes conectados {player_id: WebSocketHandler} e o estado do jogo compartilhado

# Função que envia o estado do jogo para todos os jogadores
def broadcast():
    msg = json.dumps(game_state) # Converte o estado do jogo para JSON (formato de envio)
    for client in clients.values():
        client.write_message(msg)  # Envia mensagem para cada jogador conectado
        
# Classe principal do WebSocket (controla conexão em tempo real)
class GameWebSocket(tornado.websocket.WebSocketHandler):
     # Executado quando um jogador entra no jogo
    def open(self): 
        # Limita a 2 jogadores, gera ID único, adiciona ao estado do jogo e transmite para todos
        if len(clients) >= 2:
            self.write_message(json.dumps({"error": "Sala cheia"})) # Envia mensagem de erro se já tiver 2 jogadores
            self.close() # Fecha a conexão se a sala estiver cheia
            return

        # Cria um ID único para o jogador
        player_id = str(uuid.uuid4())[:5]
        self.player_id = player_id

        # Adiciona jogador na lista de conexões
        clients[player_id] = self

        # Adiciona jogador no estado do jogo
        game_state["players"].append(player_id)

        # Define quem começa jogando (primeiro jogador)
        if game_state["current_player"] is None:
            game_state["current_player"] = player_id

        # Envia o estado do jogo + ID do jogador que entrou
        self.write_message(json.dumps({
            "state": game_state,
            "player_id": player_id
        }))

        # Atualiza todos os jogadores
        broadcast()

    # Executado quando um jogador envia uma jogada
    def on_message(self, message):
        data = json.loads(message) # Converte mensagem recebida para objeto Python

        #Restart
        if data.get("action") == "restart":
            init_game()

            if game_state["players"]:
                game_state["current_player"] = game_state["players"][0]

            game_state["winner"] = None  

            broadcast()
            return

        r, c = data["r"], data["c"]

        #Jogo já acabou
        if game_state["game_over"]:
            return

        #Não é a vez
        if self.player_id != game_state["current_player"]:
            return

        # Já clicado
        if game_state["revealed"][r][c]:
            return

        #Revela
        game_state["revealed"][r][c] = True

        #Bomba
        if game_state["board"][r][c] == 1:
            game_state["game_over"] = True
            game_state["winner"] = self.player_id
        else:
            #Troca turno
            players = game_state["players"]
            if len(players) == 2:
                idx = players.index(self.player_id)
                game_state["current_player"] = players[(idx + 1) % 2]

        broadcast()

     # Executado quando jogador sai/desconecta
    def on_close(self):
        pid = self.player_id

        # Remove da lista de conexões
        clients.pop(pid, None)

        # Remove do estado do jogo
        if pid in game_state["players"]:
            game_state["players"].remove(pid)

        print(f"Jogador {pid} desconectado")

        # Se sobrar 1 jogador, ele ganha por abandono
        if len(game_state["players"]) == 1:
            winner = game_state["players"][0]

            game_state["game_over"] = True
            game_state["winner"] = winner

        # Se não sobrar nenhum, reinicia o jogo para esperar novos jogadores
        elif len(game_state["players"]) == 0:
            init_game()

        broadcast()

     # Permite conexão de qualquer origem (evita bloqueio do navegador)
    def check_origin(self, origin):
        return True


BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # Define o diretório base para servir os arquivos estáticos

# Configuração do servidor
def make_app():
    return tornado.web.Application([
        (r"/ws", GameWebSocket),
        (r"/(.*)", tornado.web.StaticFileHandler, {
            "path": os.path.join(BASE_DIR, "client"),
            "default_filename": "index.html"
        }),
    ])

# Inicialização do servidor
if __name__ == "__main__":
    init_game() # Cria o primeiro tabuleiro

    app = make_app()
    app.listen(8000)

    print("Servidor rodando em http://localhost:8000")

    tornado.ioloop.IOLoop.current().start()