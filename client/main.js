const board = document.getElementById("board");
const status = document.getElementById("status");
const restartBtn = document.getElementById("restart");
const explosion = document.getElementById("explosion");

let myId = null;
let gameState = null;
let exploded = false;

// Áudio
const bombSound = new Audio("bomb.mp3");
bombSound.volume = 0.7;

// Explosão visual
function explodeEffect() {
    explosion.classList.remove("hidden");
    document.body.classList.add("shake");

    setTimeout(() => {
        explosion.classList.add("hidden");
        document.body.classList.remove("shake");
    }, 400);
}

// WebSocket (FUNCIONA LOCAL + NGROK)
const ws = new WebSocket(
    (location.protocol === "https:" ? "wss://" : "ws://") +
    location.host +
    "/ws"
);

// Recebe dados (com proteção contra erro)
ws.onmessage = (event) => {
    try {
        const data = JSON.parse(event.data);

        if (data.player_id && data.state) {
            myId = data.player_id;
            gameState = data.state;
        } else {
            gameState = data;
        }

        if (!gameState) return;

        updateStatus();
        render(gameState);

    } catch (e) {
        console.error("Erro no onmessage:", e);
    }
};

// Status
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

// Render (com proteção)
function render(state) {
    if (!state || !state.board || !state.revealed) return;

    board.innerHTML = "";

    state.board.forEach((row, r) => {
        row.forEach((cell, c) => {
            const btn = document.createElement("button");

            btn.className = "w-12 h-12 rounded-xl flex items-center justify-center text-lg font-bold transition shadow-md";

            if (state.revealed[r][c]) {
                if (cell === 1) {
                    btn.innerText = "💣";
                    btn.classList.add("bg-red-500");
                } else {
                    btn.innerText = "✔";
                    btn.classList.add("bg-green-500");
                }
            } else {
                btn.innerText = "?";
                btn.classList.add("bg-slate-700", "hover:bg-slate-600");
            }

            if (state.game_over || state.revealed[r][c]) {
                btn.disabled = true;
                btn.classList.add("cursor-not-allowed", "opacity-80");
            }

            btn.onclick = () => {
                if (gameState.game_over) return;
                if (gameState.current_player !== myId) return;
                if (state.revealed[r][c]) return;

                // SOM NO CLIQUE DA BOMBA
                if (state.board[r][c] === 1 && !exploded) {
                    exploded = true;

                    bombSound.currentTime = 0;
                    bombSound.play();

                    explodeEffect();
                }

                ws.send(JSON.stringify({ r, c }));
            };

            board.appendChild(btn);
        });
    });
}

// Restart
restartBtn.onclick = () => {
    exploded = false;
    ws.send(JSON.stringify({ action: "restart" }));
};