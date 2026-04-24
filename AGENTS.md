# AGENTS.md - Campo Minado Multiplayer

## Objetivo
Definir diretrizes simples para desenvolvimento do projeto, garantindo organização e consistência entre cliente e servidor.

---

## Estrutura do Projeto

ProjetoCampoMinado/
├── client/
│   ├── index.html
│   ├── main.js
│   └── bomb.mp3
│
├── server/
│   ├── game_manager.py
│   └── handler.py
│
├── main.py
└── AGENTS.md

---

## Arquitetura

### Servidor (Python + Tornado)
- Mantém o estado global do jogo (game_state)
- Controla regras (turno, vitória, fim de jogo)
- Gerencia comunicação via WebSocket

### Cliente (HTML + JavaScript)
- Interface do usuário
- Envia jogadas para o servidor
- Atualiza o tabuleiro em tempo real

---

## Regras de Desenvolvimento

- O estado do jogo deve ser controlado apenas no servidor
- O cliente não deve conter lógica de validação crítica
- Toda comunicação deve ocorrer via WebSocket
- Alterações devem manter compatibilidade com multiplayer

---

## Fluxo do Jogo

1. Jogador conecta via WebSocket
2. Recebe estado inicial
3. Envia jogadas (linha e coluna)
4. Servidor valida e atualiza o estado
5. Estado atualizado é enviado para todos
6. Em caso de bomba → jogo termina
7. Reinício via botão sem nova conexão

---

## Observações

- Projeto limitado a 2 jogadores simultâneos
- Comunicação em tempo real
- Aplicação distribuída com estado centralizado