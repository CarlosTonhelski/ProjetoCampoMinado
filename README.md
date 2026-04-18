# 💣 Campo Minado Multiplayer

Aplicação multiplayer em tempo real desenvolvida utilizando **WebSockets**, com Python no servidor e JavaScript no cliente.

---

## 📌 Tecnologias Utilizadas

- Python (Tornado) → Servidor WebSocket  
- JavaScript → Cliente  
- HTML + TailwindCSS → Interface  
- WebSocket → Comunicação em tempo real  

---

## 🎮 Funcionamento do Jogo

O jogo permite a interação simultânea de dois jogadores em um mesmo tabuleiro.

- Ao acessar a aplicação, o jogador se conecta ao servidor via WebSocket  
- O servidor mantém o estado global do jogo (tabuleiro, turnos e jogadas)  
- Cada jogador realiza jogadas clicando nos quadrados  
- O servidor valida a jogada e atualiza o estado para ambos os jogadores  

### Regras:

- O jogo é limitado a 2 jogadores  
- Os turnos são alternados entre os jogadores  
- Um quadrado só pode ser clicado uma vez  
- Ao clicar em uma bomba, o jogo termina  
- Após o fim da partida, é possível reiniciar o jogo sem criar uma nova conexão  

---

## 👥 Integrantes

- Carlos Eduardo Tonhelski, RA: 1137093
- João Vinicius Lago, RA: 1136868
- Júlia Wonsick Pazzinatto, RA: 1136562  

---

## 📚 Disciplina

Computação Distribuída  
Professor: Hiago Oliveira
