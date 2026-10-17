# MinePy

Um projeto estilo Minecraft em Python, feito com **GLFW** (janela e entrada) e **OpenGL** (desenho). A projeção 3D → 2D é implementada à mão, sem usar as funções de câmera do OpenGL.

---

## 1. Setup

### Requisitos

- Python 3.12 (é a versão testada)
- Git

### Passo a passo

**1. Clonar o repositório**

```bash
git clone <url-do-repositorio>
cd MinePy
```

**2. Criar o ambiente virtual**

O ambiente virtual (`.venv`) guarda as bibliotecas do projeto separadas do Python do sistema.

```bash
python -m venv .venv
```

**3. Ativar o ambiente virtual**

| Sistema | Comando |
|---|---|
| Windows (PowerShell) | `.venv\Scripts\Activate.ps1` |
| Windows (cmd) | `.venv\Scripts\activate.bat` |
| Linux / macOS | `source .venv/bin/activate` |

Com o ambiente ativo, aparece `(.venv)` no começo da linha do terminal.

> No PowerShell, se aparecer um erro de "execução de scripts desabilitada", rode uma vez:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

**4. Instalar as dependências**

```bash
pip install glfw PyOpenGL PyOpenGL-accelerate
```

- `glfw`: cria a janela e lê o teclado e o mouse.
- `PyOpenGL`: dá acesso às funções do OpenGL (`glClear`, `glBegin`, ...).
- `PyOpenGL-accelerate`: deixa o PyOpenGL mais rápido. É opcional.

**5. Rodar**

```bash
python base.py
```

> **VS Code:** pressione `Ctrl+Shift+P` → *Python: Select Interpreter* e escolha o `.venv`. Assim o botão de rodar usa o ambiente certo.

### Controles

| Tecla | Ação |
|---|---|
| `W` / `S` | move o cubo para cima / baixo (eixo Y) |
| `A` / `D` | move o cubo para esquerda / direita (eixo X) |
| `K` / `J` | afasta / aproxima o cubo (eixo Z) |

### Estrutura

| Arquivo | Conteúdo |
|---|---|
| `base.py` | Janela, loop do jogo, entrada e projeção (`ViewPort`, `Canvas`) |
| `geometry.py` | Formas geométricas (`Point`, `Cube`, `Plane`, `Triangle`) |

---

## 2. Conceitos de computação gráfica

### 2.1 Projeção em perspectiva

Esta é a ideia central do projeto: como transformar um ponto 3D do mundo num pixel 2D da tela.

#### O cenário

```
        Y
        │       ┌───────────┐
        │       │           │      • P (ponto no mundo)
        │       │    • P'   │    ╱
        │       │       ╲   │  ╱
        │       │         ╲ │╱
  câmera ●──────┼───────────┼────────────► Z
     (0,0,0)    │           │
                └───────────┘
                ◄─── d ────►
                 viewport
           (plano de projeção)
```

- A **câmera** fica na origem `(0, 0, 0)`, olhando na direção de **+Z**.
- A **viewport** é um retângulo no mundo 3D, a uma distância `d` da câmera. Ela tem largura `Vw` e altura `Vh`, nas mesmas unidades do mundo.
- Para desenhar um ponto **P**, traçamos uma linha de P até a câmera. O lugar onde essa linha atravessa a viewport é o **P'**, e é ali que P "aparece".

A projeção acontece em duas etapas.

#### Etapa 1: mundo → viewport

Os triângulos *câmera–P* e *câmera–P'* são semelhantes, então:

```
P'.x / d = P.x / P.z      →      P'.x = P.x · d / P.z
P'.y / d = P.y / P.z      →      P'.y = P.y · d / P.z
```

O resultado ainda está em **unidades do mundo**: é a posição de P' dentro do retângulo da viewport.

A **divisão por Z** é o que cria a perspectiva. Quanto mais longe o ponto (Z maior), menor o resultado, então objetos distantes aparecem menores e mais próximos do centro.

#### Etapa 2: viewport → canvas

O **canvas** é a janela, medida em **pixels**. Esta etapa responde: se eu esticar o retângulo da viewport até ocupar a janela toda, em qual pixel o P' cai?

```
Cx = (P'.x / Vw) · Cw
Cy = (P'.y / Vh) · Ch
```

- `P'.x / Vw` é a **fração** da viewport onde o P' está (por exemplo, 25% da largura).
- `· Cw` converte essa fração em pixels.

É como uma foto: a viewport é o filme, e o canvas é o papel onde ela é impressa. O ponto fica na mesma proporção nos dois, só muda a escala.

No código, as duas etapas ficam em `Canvas.project`:

```python
def project(self, point):
    vx = point.x / point.z * self.viewport.d    # etapa 1
    vy = point.y / point.z * self.viewport.d
    cx = vx / self.viewport.w * self.w          # etapa 2
    cy = vy / self.viewport.h * self.h
    return cx, cy
```

#### Exemplo numérico

Com `Vw = 1`, `d = 1` e `Cw = 640`:

| Ponto | P.x | P.z | P'.x = P.x · d / P.z | Cx = P'.x / Vw · Cw |
|---|---|---|---|---|
| canto da frente | 100 | 200 | 0.5 | 320 px (borda da tela) |
| canto de trás | 100 | 400 | 0.25 | 160 px |

O mesmo `x = 100` aparece com a metade do tamanho quando está duas vezes mais longe.

#### Campo de visão

O tamanho da viewport comparado com a distância `d` define **quanto do mundo a câmera enxerga**:

- `Vw = 1`, `d = 1`: cerca de 53° de campo de visão. É uma visão "normal".
- `Vw` grande ou `d` pequeno: grande-angular. Cabe mais coisa na tela e tudo aparece menor.
- `Vw` pequeno ou `d` grande: zoom, como numa teleobjetiva.

> **Erro comum:** usar a viewport do mesmo tamanho do canvas (por exemplo, `Vw = 640` com `d = 1`). Isso dá um campo de visão de quase 180° e os objetos viram pontinhos.

#### Cuidados

- **Proporção:** use `Vw / Vh = Cw / Ch`. Com uma janela de 640×480, a viewport deve ser 1 × 0.75. Se as proporções forem diferentes, a imagem fica esticada.
- **Pontos atrás da câmera:** a fórmula só vale para `Z > 0`. Com `Z = 0` ocorre divisão por zero, e com `Z < 0` o ponto aparece espelhado. Os objetos precisam ficar **na frente** da câmera.

### 2.2 Sistemas de coordenadas

Um ponto passa por vários sistemas até chegar na tela:

```
mundo (3D)  →  viewport (2D, unidades do mundo)  →  canvas (pixels)  →  NDC (-1 a 1)  →  janela
└──────────── feito pelo nosso código ──────────────────────┘   └──────── feito pelo OpenGL ────────┘
```

- **NDC** (*Normalized Device Coordinates*): internamente, o OpenGL sempre trabalha com coordenadas de **-1 a 1** nos dois eixos, com `(0, 0)` no centro.
- **`glOrtho(-320, 320, -240, 240, -1, 1)`**: diz ao OpenGL que vamos passar coordenadas em **pixels**, com a origem no centro e o Y para cima. Ele converte para NDC sozinho.
- **`glViewport`**: define em qual área da janela, em pixels, o espaço -1 a 1 é desenhado. O GLFW já configura isso com o tamanho da janela.

> **Não confunda:** o `glViewport` do OpenGL faz o papel do nosso *canvas*. A *viewport* do nosso código é o plano de projeção no mundo 3D.

### 2.3 Triângulos e primitivas

Toda superfície 3D é desenhada como um conjunto de **triângulos**. No projeto:

```
Cube  →  6 Planes (faces)  →  2 Triangles cada  →  12 triângulos
```

O OpenGL desenha a partir de vértices, e a **primitiva** passada para o `glBegin` diz como interpretá-los:

| Primitiva | Significado |
|---|---|
| `GL_POINTS` | cada vértice é um ponto |
| `GL_LINES` | cada 2 vértices formam uma linha |
| `GL_LINE_LOOP` | liga os vértices em sequência e fecha no primeiro (contorno) |
| `GL_TRIANGLES` | cada 3 vértices formam um triângulo preenchido |

Para ver só o contorno de todos os triângulos (**wireframe**), dá para usar `glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)`. Isso ajuda a depurar a malha.

**Rasterização** é o processo de descobrir quais pixels ficam dentro de cada triângulo e pintá-los. A placa de vídeo faz isso automaticamente.

### 2.4 O loop do jogo

O jogo roda num `while` em que cada volta é um **frame**:

```python
while not glfw.window_should_close(window):
    update()                    # lógica: entrada, movimento
    draw()                      # limpa a tela e desenha tudo
    glfw.swap_buffers(window)   # mostra o frame
    glfw.poll_events()          # processa teclado, mouse, janela
```

**Limpar a tela:**

- `glClearColor(r, g, b, a)` define a cor de fundo, com valores de 0 a 1. Basta chamar uma vez.
- `glClear(GL_COLOR_BUFFER_BIT)` pinta a tela inteira com essa cor. É chamado no começo de todo frame, senão o desenho novo fica por cima do anterior.
- Em 3D com teste de profundidade, também se limpa o *depth buffer*: `glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)`.

**Double buffering:** a janela tem dois buffers de cor.

- O **front buffer** é o que está aparecendo na tela.
- O **back buffer** é onde o frame está sendo desenhado, escondido.

O `swap_buffers` troca os dois. Assim a tela só mostra frames completos, sem piscar.

**`poll_events`:** lê a fila de eventos do sistema operacional. Sem ele, o teclado não responde, o botão de fechar não funciona e o Windows acha que o programa travou.

**Delta time (`dt`):** o loop roda o mais rápido possível, então o FPS varia de um computador para outro. Para o movimento ter a mesma velocidade em qualquer máquina, multiplicamos a velocidade pelo tempo que passou desde o último frame:

```python
dt = agora - ultimo_frame
deslocamento = velocidade * dt     # unidades por segundo, não por frame
```

**Contexto OpenGL:** toda função `gl...` só funciona depois de `glfw.make_context_current(window)`. Antes disso, o OpenGL não sabe em que janela desenhar e dá erro 1282 (*invalid operation*).
