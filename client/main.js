const board = document.getElementById("board");
const status = document.getElementById("status");
const restartBtn = document.getElementById("restart");
const explosion = document.getElementById("explosion");

let myId = null; // 
let gameState = null; // Estado do jogo recebido do servidor
let exploded = false; // Flag para evitar múltiplas explosões

const bombSound = new Audio("bomb.mp3");
bombSound.volume = 0.7;

//Explosão
function explodeEffect() {
    explosion.classList.remove("hidden");
    document.body.classList.add("shake");

    setTimeout(() => {
        explosion.classList.add("hidden");
        document.body.classList.remove("shake");
    }, 400);
}

//Websocket
const ws = new WebSocket(
    location.protocol === "https:"
        ? "wss://" + location.host + "/ws" // Usa wss para conexões seguras
        : "ws://" + location.host + "/ws" // Usa ws para conexão local
);

//Recebe dados -> Recebe estado do jogo e ID do jogador
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);

    if (data.player_id) {
        myId = data.player_id;
        gameState = data.state;
    } else {
        gameState = data;
    }

    updateStatus();
    render(gameState);
};

//Status -> Atualiza o status do jogo (turno, vitória, derrota)
function updateStatus() {
    if (!gameState || !myId) return;

    if (gameState.game_over) {
        restartBtn.classList.remove("hidden");

        if (gameState.winner === myId) {
            status.innerText = "Você venceu!";
        } else {
            status.innerText = "Você perdeu!";
        }
        return;
    }

    restartBtn.classList.add("hidden");

    if (gameState.current_player === myId) {
        status.innerText = "🟢 Sua vez!";
    } else {
        status.innerText = "⏳ Aguardando jogada do oponente...";
    }
}

//Render -> Renderiza o tabuleiro do jogo
function render(state) {
    board.innerHTML = ""; // Limpa o tabuleiro antes de renderizar

    // Percorre o tabuleiro e cria os botões para cada célula
    state.board.forEach((row, r) => {
        row.forEach((cell, c) => {
            const btn = document.createElement("button");

            btn.className = "w-12 h-12 rounded-xl flex items-center justify-center text-lg font-bold transition shadow-md";

            if (state.revealed[r][c]) { // Se revelado, bomba = vermelho, seguro = verde
                if (cell === 1) {
                    btn.innerText = "💣";
                    btn.classList.add("bg-red-500");
                } else {
                    btn.innerText = "✔";
                    btn.classList.add("bg-green-500");
                }
            } else {
                btn.innerText = "?"; // Se não revelado
                btn.classList.add("bg-slate-700", "hover:bg-slate-600");
            }

            // Trava o jogo
            if (state.game_over || state.revealed[r][c]) {
                btn.disabled = true; // Se ja cliclado ou jogo acabou
                btn.classList.add("cursor-not-allowed", "opacity-80");
            }

            btn.onclick = () => { // Ao clicar, verifica se o jogo acabou, se é a vez do jogador e se a célula já foi revelada
                if (gameState.game_over) return;
                if (gameState.current_player !== myId) return;
                if (state.revealed[r][c]) return;

                if (state.board[r][c] === 1 && !exploded) { // Se clicar na bomba, toca som e a explsão
                    exploded = true;

                    bombSound.currentTime = 0;
                    bombSound.play();

                    explodeEffect();
                }

                ws.send(JSON.stringify({ r, c })); // Envia a jogada para o servidor
            };

            board.appendChild(btn);
        });
    });
}

//Restart
restartBtn.onclick = () => {
    exploded = false;
    ws.send(JSON.stringify({ action: "restart" }));
};