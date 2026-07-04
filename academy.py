import sys
import time
import math
import random
import numpy as np
import cv2
from collections import namedtuple

print("=== ACADEMY.PY - RRT COM VISUALIZAÇÃO ===", flush=True)
sys.stdout.flush()

# ============================================================
# 1. IMPORTAÇÕES
# ============================================================
try:
    import HAL
    print("[OK] HAL importado.", flush=True)
except Exception as e:
    print(f"[ERRO] HAL: {e}", flush=True)
    sys.exit(1)

try:
    from WebGUI import WebGUI
    print("[OK] WebGUI importado.", flush=True)
except Exception as e:
    print(f"[ERRO] WebGUI: {e}", flush=True)
    sys.exit(1)

# ============================================================
# 2. FUNÇÃO PARA OBTER MAPA (fallback sintético)
# ============================================================
def get_map():
    urls = [
        "ws://localhost:7164",
        "ws://127.0.0.1:7164",
        "ws://webgui:7164",
        "ws://host.docker.internal:7164",
        "ws://172.17.0.1:7164",
        "http://localhost:7164",
        "http://127.0.0.1:7164",
        "http://webgui:7164",
    ]
    for url in urls:
        try:
            print(f"[TEST] Tentando URL: {url}", flush=True)
            gui = WebGUI()
            map_array = gui.getMap(url)
            if map_array is not None and hasattr(map_array, 'shape') and map_array.size > 0:
                print(f"[SUCESSO] Mapa obtido com URL: {url}", flush=True)
                print(f"  Shape: {map_array.shape}", flush=True)
                return map_array, gui, url
        except Exception as e:
            print(f"  Falha: {e}", flush=True)
    # Fallback: mapa sintético
    print("[INFO] Gerando mapa sintético (fallback).", flush=True)
    img = np.ones((600, 1000), dtype=np.uint8) * 255
    cv2.rectangle(img, (100, 100), (250, 300), 0, -1)
    cv2.rectangle(img, (400, 350), (550, 500), 0, -1)
    cv2.rectangle(img, (700, 50), (900, 200), 0, -1)
    cv2.rectangle(img, (50, 450), (150, 550), 0, -1)
    cv2.rectangle(img, (850, 400), (950, 550), 0, -1)
    cv2.imwrite("mapa_sintetico_base.png", img)
    print("[INFO] Mapa sintético salvo como mapa_sintetico_base.png", flush=True)
    occupancy = (img < 128).astype(np.uint8)
    gui = WebGUI()
    return occupancy, gui, None

# ============================================================
# 3. NODE E RRTPlanner (com desenho em imagem)
# ============================================================
Node = namedtuple('Node', ['x', 'y', 'parent'])

class RRTPlanner:
    def __init__(self, map_array, step_size=15, goal_bias=0.2, max_iter=4000):
        self.map = map_array
        self.step_size = step_size
        self.goal_bias = goal_bias
        self.max_iter = max_iter
        self.tree = []
        self.path = []

    def sample_random_point(self, goal):
        if random.random() < self.goal_bias:
            return goal
        h, w = self.map.shape[:2]
        return (random.randint(0, w-1), random.randint(0, h-1))

    def find_nearest_node(self, point):
        nearest = self.tree[0]
        min_dist = self.distance(nearest, point)
        for node in self.tree:
            d = self.distance(node, point)
            if d < min_dist:
                min_dist = d
                nearest = node
        return nearest

    def steer(self, from_node, to_point):
        dx = to_point[0] - from_node.x
        dy = to_point[1] - from_node.y
        dist = math.hypot(dx, dy)
        if dist <= self.step_size:
            return to_point
        scale = self.step_size / dist
        return (int(from_node.x + dx * scale), int(from_node.y + dy * scale))

    def is_collision_free(self, from_node, to_point):
        steps = int(max(abs(to_point[0] - from_node.x),
                        abs(to_point[1] - from_node.y)))
        if steps == 0:
            return True
        for i in range(steps + 1):
            t = i / steps
            x = int(from_node.x + t * (to_point[0] - from_node.x))
            y = int(from_node.y + t * (to_point[1] - from_node.y))
            if x < 0 or y < 0 or y >= self.map.shape[0] or x >= self.map.shape[1]:
                return False
            if self.map[y, x] > 0.5:
                return False
        return True

    def reconstruct_path(self, goal_node):
        path = []
        current = goal_node
        while current is not None:
            path.append((current.x, current.y))
            current = current.parent
        return path[::-1]

    def plan(self, start, goal, gui=None, url=None):
        self.tree = [Node(start[0], start[1], None)]
        self.path = []
        for i in range(self.max_iter):
            rnd = self.sample_random_point(goal)
            nearest = self.find_nearest_node(rnd)
            new_point = self.steer(nearest, rnd)
            if self.is_collision_free(nearest, new_point):
                new_node = Node(new_point[0], new_point[1], nearest)
                self.tree.append(new_node)
                # A cada 100 iterações, imprime progresso
                if i % 500 == 0 and i > 0:
                    print(f"[RRT] Iteração {i}, nós: {len(self.tree)}", flush=True)
                if self.distance(new_node, goal) < self.step_size * 1.5:
                    if self.is_collision_free(new_node, goal):
                        goal_node = Node(goal[0], goal[1], new_node)
                        self.tree.append(goal_node)
                        self.path = self.reconstruct_path(goal_node)
                        return True
        return False

    def distance(self, node, point):
        return math.hypot(node.x - point[0], node.y - point[1])

# ============================================================
# 4. FUNÇÃO PARA DESENHAR ÁRVORE E CAMINHO EM IMAGEM
# ============================================================
def draw_tree_and_path_on_image(map_img, tree, path, color_tree=(0,255,0), color_path=(0,0,255)):
    # map_img deve ser uma imagem BGR (3 canais)
    img = map_img.copy()
    # Desenha árvore em verde
    for node in tree:
        if node.parent is not None:
            cv2.line(img, (node.x, node.y), (node.parent.x, node.parent.y), color_tree, 1)
    # Desenha caminho em vermelho (mais grosso)
    for i in range(len(path)-1):
        cv2.line(img, (path[i][0], path[i][1]), (path[i+1][0], path[i+1][1]), color_path, 2)
    return img

# ============================================================
# 5. FUNÇÃO PRINCIPAL
# ============================================================
import os
print("[DEBUG] Diretório atual:", os.getcwd())
def main():
    print("[MAIN] Iniciando...", flush=True)

    # Obtém mapa (WebGUI ou sintético)
    occupancy, gui, url = get_map()
    print(f"[MAIN] Mapa: {occupancy.shape}, livres: {np.sum(occupancy==0)}, obst: {np.sum(occupancy==1)}", flush=True)

    # Converte ocupação (0/1) para imagem BGR para desenho
    # 0 = livre (branco), 1 = obstáculo (preto)
    map_img = np.ones((occupancy.shape[0], occupancy.shape[1], 3), dtype=np.uint8) * 255
    map_img[occupancy == 1] = [0, 0, 0]  # obstáculos em preto

    # Define start e goal (para mapa sintético 600x1000)
    start = (50, 50)
    goal  = (950, 580)

    # Se o mapa for real (diferente), ajusta coordenadas
    if occupancy.shape != (600, 1000):
        h, w = occupancy.shape
        start = (int(w*0.1), int(h*0.1))
        goal  = (int(w*0.9), int(h*0.9))
        # Busca pontos livres
        for dx in range(20):
            for dy in range(20):
                nx, ny = start[0]+dx, start[1]+dy
                if 0 <= nx < w and 0 <= ny < h and occupancy[ny, nx] == 0:
                    start = (nx, ny)
                    break
            if occupancy[start[1], start[0]] == 0:
                break
        for dx in range(20):
            for dy in range(20):
                nx, ny = goal[0]-dx, goal[1]-dy
                if 0 <= nx < w and 0 <= ny < h and occupancy[ny, nx] == 0:
                    goal = (nx, ny)
                    break
            if occupancy[goal[1], goal[0]] == 0:
                break

    print(f"[MAIN] Start: {start}, Goal: {goal}", flush=True)

    if occupancy[start[1], start[0]] != 0:
        print("[ERRO] Start em obstáculo!", flush=True)
        return
    if occupancy[goal[1], goal[0]] != 0:
        print("[ERRO] Goal em obstáculo!", flush=True)
        return
    print("[MAIN] Start e Goal livres.", flush=True)

    # Planejador
    planner = RRTPlanner(occupancy, step_size=18, goal_bias=0.15, max_iter=5000)
    success = planner.plan(start, goal, gui=gui, url=url)

    if not success:
        print("[MAIN] Planejamento falhou.", flush=True)
        return

    path = planner.path
    tree = planner.tree
    print(f"[MAIN] Caminho encontrado com {len(path)} pontos.", flush=True)

    # Desenha árvore e caminho na imagem do mapa
    img_with_tree = draw_tree_and_path_on_image(map_img, tree, path)
    cv2.imwrite("mapa_com_arvore.png", img_with_tree)
    print("[DEBUG] Tentando salvar em:", os.getcwd() + "/mapa_com_arvore.png")
    print("[INFO] Imagem 'mapa_com_arvore.png' salva com árvore (verde) e caminho (vermelho).", flush=True)

    # Navegação (igual ao anterior)
    target_idx = 1
    while target_idx < len(path):
        try:
            pose = HAL.getPose3d()
            robot_x = pose.x
            robot_y = pose.y
            robot_yaw = pose.yaw

            wp_px, wp_py = path[target_idx]
            if url:
                wp_world = WebGUI.mapToWorld(url, wp_px, wp_py)
            else:
                wp_world = (wp_px * 0.01, wp_py * 0.01)

            dx = wp_world[0] - robot_x
            dy = wp_world[1] - robot_y
            dist = math.hypot(dx, dy)

            if dist < 0.3:
                target_idx += 1
                print(f"[NAV] Waypoint {target_idx-1} ok. Restam {len(path)-target_idx}", flush=True)
                continue

            desired = math.atan2(dy, dx)
            error = desired - robot_yaw
            error = (error + math.pi) % (2*math.pi) - math.pi

            angular = 2.0 * error
            angular = max(-2.0, min(2.0, angular))

            HAL.setV(0.8)
            HAL.setW(angular)
            time.sleep(0.02)

        except Exception as e:
            print(f"[ERRO] Navegação: {e}", flush=True)
            break

    print("[MAIN] 🏁 Destino alcançado!", flush=True)
    HAL.setV(0.0)
    HAL.setW(0.0)

if __name__ == "__main__":
    main()
    print("=== FIM DO SCRIPT ===", flush=True)
