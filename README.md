# 🤖 Planejamento de Caminho com RRT (Rapidly-exploring Random Tree)

Implementação do algoritmo **Rapidly-exploring Random Tree (RRT)** desenvolvida para a disciplina de **Robótica Móvel**, utilizando o ambiente **RoboticsAcademy (JdeRobot)**.

O objetivo do projeto é realizar o planejamento de caminho entre uma posição inicial e um objetivo em um ambiente contendo obstáculos, além de simular a navegação do robô seguindo o caminho encontrado.

---

## 📚 Sobre o algoritmo

O **RRT (Rapidly-exploring Random Tree)** é um algoritmo de planejamento baseado em amostragem amplamente utilizado em:

- 🚗 Veículos autônomos
- 🤖 Robôs móveis
- 🦾 Braços robóticos
- 🚁 Drones
- 🚀 Sistemas de navegação

Ao contrário de algoritmos clássicos como **A\***, o RRT **não necessita de um grafo previamente construído**. Ele cria uma árvore de exploração de forma incremental até encontrar uma rota livre de colisões.

---

# 🎯 Objetivos do projeto

Implementar do zero uma versão didática do algoritmo RRT capaz de:

- Construir uma árvore de exploração;
- Encontrar um caminho entre início e objetivo;
- Evitar obstáculos durante o planejamento;
- Reconstruir o caminho encontrado;
- Simular a navegação do robô utilizando os waypoints gerados.

---

# ⚙️ Funcionalidades implementadas

✔ Geração de pontos aleatórios

✔ Goal Biasing

✔ Busca do nó mais próximo

✔ Função Steer

✔ Verificação de colisão

✔ Reconstrução do caminho

✔ Planejamento completo (plan)

✔ Navegação do robô

✔ Visualização da árvore RRT

✔ Visualização do caminho final

---

# 🧠 Estrutura do algoritmo

Cada nó da árvore é composto por:

```python
Node(
    x,
    y,
    parent
)
```

onde:

- **x** → coordenada horizontal
- **y** → coordenada vertical
- **parent** → referência ao nó pai para reconstrução do caminho.

---

# 🔄 Fluxo de execução

```text
Mapa de ocupação
        │
        ▼
Inicialização do RRT
        │
        ▼
Amostragem aleatória
(sample_random_point)
        │
        ▼
Busca do nó mais próximo
(find_nearest_node)
        │
        ▼
Expansão da árvore
(steer)
        │
        ▼
Teste de colisão
(is_collision_free)
        │
        ▼
Adicionar novo nó
        │
        ▼
Objetivo alcançado?
        │
    Não │ Sim
        ▼
Reconstrução do caminho
        │
        ▼
Navegação do robô
```

---

# 📂 Estrutura do projeto

```
global_navigation/

├── academy.py              # Implementação principal
├── academy.cpp             # Arquivo original do template
├── mapa_com_arvore.png     # Árvore RRT e caminho encontrado
├── README.md
└── relatorio.pdf
```

---

# 🖼 Resultado

Durante a execução são produzidas duas visualizações principais:

🟢 **Árvore RRT**

- representa toda a exploração realizada pelo algoritmo.

🔴 **Caminho Final**

- representa a sequência de nós utilizada pelo robô até o objetivo.

---

# 🚗 Navegação

Após o planejamento, o robô percorre o caminho utilizando um controlador proporcional simples.

Para cada waypoint são calculados:

- direção desejada;
- erro angular;
- velocidade angular;
- velocidade linear constante.

O processo continua até atingir o objetivo.

---

# 💻 Tecnologias utilizadas

- Python 3
- NumPy
- OpenCV
- RoboticsAcademy
- ROS 2
- JdeRobot

---

# 📈 Algoritmos implementados

- Random Sampling
- Goal Biasing
- Nearest Neighbor Search
- Steer
- Collision Checking
- Path Reconstruction

---

# 📌 Limitações

Esta implementação representa uma versão didática do algoritmo RRT.

As seguintes simplificações foram adotadas:

- robô tratado como um ponto;
- planejamento apenas em (x,y);
- movimento holonômico;
- ausência de dilatação dos obstáculos;
- controlador de navegação simplificado.

---

# 📷 Exemplo de saída

<p align="center">
  <img src="mapa_com_arvore.png" width="800">
</p>

---

# 👩‍💻 Autora

**Mariana Lins**

Projeto desenvolvido para a disciplina de **Robótica Móvel**.

Universidade Federal de Alagoas (UFAL)

---

# 📄 Licença

Este projeto foi desenvolvido exclusivamente para fins acadêmicos.
