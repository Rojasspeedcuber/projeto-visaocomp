# 🎮 Body Motion Game - Jogo Controlado por Visão Computacional

Jogo de desviar de obstáculos controlado inteiramente pelos movimentos do corpo, capturados através da webcam usando visão computacional.

## 🎯 Objetivo

Desvie dos obstáculos que caem do topo da tela movendo seu corpo em frente à câmera!

## 🕹️ Como Jogar

### Controles Corporais

- **Mover lateralmente**: Mova seu corpo para esquerda/direita
- **Pular**: Levante ambos os braços acima da cabeça
- **Agachar**: Flexione os joelhos e abaixe o corpo

### Teclas do Teclado

- `D`: Ativa/desativa modo debug
- `C`: Mostra/oculta overlay da câmera
- `R`: Reinicia o jogo (após Game Over)
- `Q` ou `ESC`: Sair do jogo

## 🛠️ Tecnologias Utilizadas

- **Python 3.8+**
- **OpenCV**: Captura de vídeo da webcam
- **MediaPipe Pose**: Rastreamento corporal em tempo real
- **Pygame**: Renderização do jogo
- **NumPy**: Processamento numérico

## 📦 Instalação

### 1. Clone ou baixe o projeto

```bash
cd projeto-visaocomp
```

### 2. Crie um ambiente virtual (recomendado)

```bash
python -m venv venv
```

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

## 🚀 Executar o Jogo

```bash
python main.py
```

## 📁 Estrutura do Projeto

```
projeto-visaocomp/
│
├── main.py              # Loop principal do jogo
├── pose_tracker.py      # Detecção de pose com MediaPipe
├── game_logic.py        # Lógica e estados do jogo
├── player.py            # Classe do jogador
├── obstacles.py         # Geração e gerenciamento de obstáculos
├── requirements.txt     # Dependências do projeto
└── README.md           # Este arquivo
```

## 🎮 Como Funciona

### 1. Detecção de Pose (MediaPipe)

O MediaPipe Pose detecta 33 pontos-chave do corpo humano em tempo real:

- **Rastreamento**: Identifica articulações como ombros, cotovelos, punhos, quadris, joelhos
- **Normalização**: Coordenadas normalizadas (0-1) independentes da resolução
- **Confiança**: Filtra detecções com baixa confiança

### 2. Calibração Inicial

Ao iniciar o jogo, há uma fase de calibração (30 frames):

- Captura posição neutra do usuário
- Estabelece linha de base para ombros e quadris
- Necessário para detectar movimentos relativos

### 3. Mapeamento de Movimentos

**Movimento Lateral:**
- Calcula centro do corpo (média dos ombros)
- Mapeia posição X (0-1) para largura da tela
- Suavização aplicada para movimento fluido

**Pulo:**
- Detecta quando punhos estão acima dos ombros
- Ativa física de pulo (gravidade + velocidade)
- Previne pulo duplo

**Agachar:**
- Compara altura atual do quadril com baseline
- Reduz altura do personagem
- Desativado durante pulo

### 4. Sistema de Jogo

**Obstáculos:**
- 3 tipos: alto, médio, baixo
- Spawn aleatório em posição X
- Velocidade aumenta com pontuação

**Dificuldade Progressiva:**
- Velocidade dos obstáculos aumenta gradualmente
- Taxa de spawn acelera com o tempo
- Sistema de pontuação por tempo sobrevivido

**Detecção de Colisão:**
- Retângulos de colisão para jogador e obstáculos
- Game Over ao colidir
- Sistema de reinício

## 🐛 Modo Debug

Ative com a tecla `D` para visualizar:

- Pontos do corpo detectados
- Coordenadas X do jogador
- Estados de pulo/agachamento
- Número de obstáculos ativos
- Janela separada com landmarks

## 🔧 Personalizações Possíveis

### Ajustar Sensibilidade

Em `pose_tracker.py`:

```python
# Pulo mais fácil (linha ~76)
self.is_jumping = avg_wrist_y < avg_shoulder_y - 0.05  # Era 0.1

# Agachar mais sensível (linha ~84)
self.is_crouching = avg_hip_y > self.baseline_hip_y + 0.05  # Era 0.08
```

### Modificar Dificuldade

Em `obstacles.py`:

```python
# Spawn mais rápido
self.base_spawn_rate = 40  # Era 60

# Velocidade inicial maior
self.base_speed = 6  # Era 4
```

**Desenvolvido com:** Python + OpenCV + MediaPipe + Pygame

**Divirta-se jogando! 🎮🚀**
