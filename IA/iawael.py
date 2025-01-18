
import random

class IA_Bomber:
    """
    IA pour un jeu de type Bomberman, prenant en compte:
    - Les minerais (M) à détruire pour gagner des points
    - Les bombes et leur explosion
    - Les fantômes (danger, possibilité de les tuer avec une bombe)
    """

    def __init__(self, num_joueur: int, game_dic: dict, timerglobal: int, timerfantôme: int) -> None:
        """
        Initialise l'IA avec le numéro de joueur et des paramètres de temps.
        :param num_joueur: Identifiant du bomber contrôlé par l’IA.
        :param game_dic: État initial du jeu.
        :param timerglobal: Nombre total de tours avant la fin de la partie.
        :param timerfantôme: Intervalle de tours pour l’apparition des fantômes.
        """
        self.num_joueur = num_joueur
        self.timerglobal = timerglobal
        self.timerfantôme = timerfantôme
        self.analyze_game_dict(game_dic)

    def analyze_game_dict(self, game_dict: dict) -> None:
        """Analyse préliminaire du dictionnaire de jeu (peu utilisée ici)."""
        pass

    # -------------------------------------------------------------------------
    # 1) MÉTHODES UTILITAIRES : FONCTIONS DE DÉTECTION ET CALCULS
    # -------------------------------------------------------------------------
    def flood_fill(self, game_dict: dict) -> list[tuple[tuple[int, int], int]]:
        """
        Calcule la distance vers les minerais ("M") en utilisant un parcours en largeur.
        Retourne une liste de ((x, y), distance) triée par distance puis par proximité
        du centre de la carte, limitée aux 10 premiers éléments.
        """
        carte = game_dict["map"]
        h, w = len(carte), len(carte[0])

        # Trouver la position du bomber contrôlé
        pos_bomber = None
        for b in game_dict["bombers"]:
            if b["num_joueur"] == self.num_joueur:
                pos_bomber = b["position"]
                break
        if not pos_bomber:
            return []

        dist = [[-1]*w for _ in range(h)]
        dist[pos_bomber[1]][pos_bomber[0]] = 0
        queue = [(pos_bomber[0], pos_bomber[1])]
        minerais = []

        while queue:
            x, y = queue.pop(0)
            if carte[y][x] == "M":
                minerais.append(((x, y), dist[y][x]))

            for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and dist[ny][nx] == -1 and carte[ny][nx] != "C":
                    # Empêcher collisions avec bombers ou bombes
                    collision = False
                    for b in game_dict["bombers"]:
                        if b["position"] == (nx, ny):
                            collision = True
                            break
                    for bomb in game_dict.get("bombes", []):
                        if bomb["position"] == (nx, ny):
                            collision = True
                            break
                    if not collision:
                        dist[ny][nx] = dist[y][x] + 1
                        queue.append((nx, ny))

        # Trier par distance puis par proximité du centre
        cx, cy = w // 2, h // 2
        minerais.sort(key=lambda m: (m[1], abs(m[0][0] - cx) + abs(m[0][1] - cy)))
        return minerais[:10]

    def can_move_to(self, pos: tuple[int,int], direction: str, game_dict: dict) -> bool:
        """
        Vérifie si l'on peut se déplacer depuis `pos` dans la direction donnée,
        en tenant compte des obstacles, bombers et bombes.
        """
        x, y = pos
        nx, ny = x, y
        if direction == "H":
            ny -= 1
        elif direction == "B":
            ny += 1
        elif direction == "G":
            nx -= 1
        elif direction == "D":
            nx += 1

        h, w = len(game_dict["map"]), len(game_dict["map"][0])
        if not (0 <= nx < w and 0 <= ny < h):
            return False
        if game_dict["map"][ny][nx] == "C":
            return False

        # Pas d’autre bomber ni bombe sur la case
        for b in game_dict["bombers"]:
            if b["position"] == (nx, ny):
                return False
        for bomb in game_dict.get("bombes", []):
            if bomb["position"] == (nx, ny):
                return False

        return True

    def get_direction_to_target(self, current_pos: tuple[int,int], target_pos: tuple[int,int], game_dict: dict) -> str:
        """
        Calcule la direction à suivre pour aller de current_pos à target_pos 
        via un BFS, en évitant les obstacles et bombers. Gère un blocage 
        si on n'avance plus depuis plusieurs tours.
        """
        self.blocked_counter = getattr(self, "blocked_counter", 0)
        self.last_position = getattr(self, "last_position", None)

        # Gestion du blocage
        if self.last_position == current_pos:
            self.blocked_counter += 1
        else:
            self.blocked_counter = 0

        if self.blocked_counter > 3:
            self.blocked_counter = 0
            dx = target_pos[0] - current_pos[0]
            dy = target_pos[1] - current_pos[1]
            if abs(dx) > abs(dy):
                pref = ["D" if dx > 0 else "G", "B" if dy > 0 else "H"]
            else:
                pref = ["B" if dy > 0 else "H", "D" if dx > 0 else "G"]
            for d in pref + ["H","B","G","D"]:
                if self.can_move_to(current_pos, d, game_dict):
                    return d

        self.last_position = current_pos

        # BFS
        H, W = len(game_dict["map"]), len(game_dict["map"][0])
        dist = [[-1]*W for _ in range(H)]
        parents = [[None]*W for _ in range(H)]
        dist[current_pos[1]][current_pos[0]] = 0
        queue = [(current_pos[0], current_pos[1])]
        found = False

        while queue and not found:
            x, y = queue.pop(0)
            if (x, y) == target_pos:
                found = True
                break

            for d in ["H","B","G","D"]:
                if not self.can_move_to((x, y), d, game_dict):
                    continue
                nx, ny = x, y
                if d == "H": ny -= 1
                elif d == "B": ny += 1
                elif d == "G": nx -= 1
                elif d == "D": nx += 1

                # Vérifier si la case est trop proche d'un fantôme
                if self.est_case_proche_fantome((nx, ny), game_dict):
                    continue

                if dist[ny][nx] == -1:
                    dist[ny][nx] = dist[y][x] + 1
                    parents[ny][nx] = (x, y, d)
                    queue.append((nx, ny))

        if found:
            x, y = target_pos
            while parents[y][x] is not None:
                px, py, d = parents[y][x]
                if (px, py) == current_pos:
                    return d
                x, y = px, py
        return "N"

    def get_safe_distance(self, bomb_pos: tuple[int,int], current_pos: tuple[int,int], portee: int = 2) -> bool:
        """
        Vérifie si `current_pos` n'est pas trop proche d'une bombe `bomb_pos`.
        On juge dangereux si c'est la même ligne/colonne avec distance <= portee+1.
        """
        if current_pos[0] == bomb_pos[0] or current_pos[1] == bomb_pos[1]:
            distance = abs(current_pos[0] - bomb_pos[0]) + abs(current_pos[1] - bomb_pos[1])
            return distance > portee + 1
        return True

    def count_adjacent_minerals(self, pos: tuple[int,int], game_dict: dict) -> int:
        """
        Nombre de minerais "M" directement adjacents (H,B,G,D) à `pos`.
        """
        c = 0
        for dx, dy in [(0,1),(1,0),(0,-1),(-1,0)]:
            nx, ny = pos[0] + dx, pos[1] + dy
            if 0 <= ny < len(game_dict["map"]) and 0 <= nx < len(game_dict["map"][0]):
                if game_dict["map"][ny][nx] == "M":
                    c += 1
        return c

    def get_safe_direction(self, pos: tuple[int,int], bombes: list[dict], carte: list[list[str]]) -> str:
        """
        Détermine la direction la plus sûre pour échapper aux explosions
        potentielles des bombes. Analyse les zones alignées sur la bombe.
        """
        dirs = {"H": (0, -1), "B": (0, 1), "G": (-1, 0), "D": (1, 0)}
        best_dir = "N"
        best_score = -1

        # Zones dangereuses
        danger_zones = set()
        for b in bombes:
            bx, by = b["position"]
            p = b["portée"]
            for dx in range(-p, p+1):
                if 0 <= bx + dx < len(carte[0]):
                    danger_zones.add((bx + dx, by))
            for dy in range(-p, p+1):
                if 0 <= by + dy < len(carte):
                    danger_zones.add((bx, by + dy))

        for d, (dx, dy) in dirs.items():
            nx, ny = pos[0] + dx, pos[1] + dy
            if not (0 <= nx < len(carte[0]) and 0 <= ny < len(carte)):
                continue
            if carte[ny][nx] == "C":
                continue

            score = 0
            if (nx, ny) not in danger_zones:
                score += 5
            for b in bombes:
                bx, by = b["position"]
                old_dist = abs(pos[0] - bx) + abs(pos[1] - by)
                new_dist = abs(nx - bx) + abs(ny - by)
                if new_dist > old_dist:
                    score += 2

            if score > best_score:
                best_score = score
                best_dir = d

        return best_dir

    # -------------------------------------------------------------------------
    # 2) FONCTIONS POUR GÉRER LES FANTÔMES
    # -------------------------------------------------------------------------
    def get_nearby_ghosts(self, bomber_pos: tuple[int,int], game_dict: dict) -> list[tuple[int,int,int]]:
        """
        Renvoie une liste de fantômes proches de la position du bomber, sous forme 
        de tuples (distance, x, y), triés par distance croissante.
        """
        ghosts = []
        for f in game_dict.get("fantômes", []):
            fx, fy = f["position"]
            dist = abs(bomber_pos[0] - fx) + abs(bomber_pos[1] - fy)
            ghosts.append((dist, fx, fy))
        ghosts.sort(key=lambda g: g[0])  # tri par distance
        return ghosts

    def can_bomb_ghost(
        self, bomber_pos: tuple[int,int], ghost_pos: tuple[int,int], game_dict: dict
    ) -> bool:
        """
        Vérifie si un fantôme est aligné (même ligne ou même colonne) et 
        suffisamment proche pour être tué par une bombe (portée = 2 + niveau//2).
        On suppose que si c'est le cas, on retournera True pour poser la bombe, 
        à condition qu'une voie de fuite existe.
        """
        bx, by = bomber_pos
        gx, gy = ghost_pos

        # Retrouver le niveau du bomber contrôlé pour estimer la portée
        bomber_niveau = 0
        for b in game_dict["bombers"]:
            if b["num_joueur"] == self.num_joueur:
                bomber_niveau = b["niveau"]
                break
        portee = 2 + bomber_niveau // 2

        if bx == gx:  # même colonne
            if abs(by - gy) <= portee:
                return True
        if by == gy:  # même ligne
            if abs(bx - gx) <= portee:
                return True
        return False

    def decide_ghost_action(self, bomber_pos: tuple[int,int], game_dict: dict) -> str:
        """
        Détermine s'il faut fuir ou poser une bombe contre un fantôme dangereux.
        1) Si un fantôme est à portée de bombe (même ligne/colonne, distance <= portée)
           ET on peut fuir après la pose, on pose la bombe.
        2) Sinon, s'il y a un fantôme adjacent (dist=1), on essaie de fuir.
        3) Sinon, pas d'action spéciale -> "N".
        """
        nearby_ghosts = self.get_nearby_ghosts(bomber_pos, game_dict)
        if not nearby_ghosts:
            return "N"

        # 1) Tenter de tuer un fantôme avec une bombe s'il est aligné et pas trop loin
        for dist_g, gx, gy in nearby_ghosts:
            if dist_g <= 2:  
                # Vérifier alignement et possibilité de fuir
                if self.can_bomb_ghost(bomber_pos, (gx, gy), game_dict):
                    # Vérifier qu'on a une direction sûre
                    safe_dir = self.get_safe_direction(bomber_pos, game_dict["bombes"], game_dict["map"])
                    if safe_dir != "N":
                        # On pose la bombe et on recule
                        self.compte_recul = 3
                        self.derniere_bombe = bomber_pos
                        return "X"

        # 2) S'il y a un fantôme adjacent (distance = 1), fuir 
        # (sauf si on a déjà posé une bombe au dessus, dans ce cas on fuira à l'étape globale)
        if nearby_ghosts[0][0] == 1:
            # Trouver une direction de fuite
            fuite = self.get_safe_direction(bomber_pos, game_dict["bombes"], game_dict["map"])
            if fuite != "N":
                return fuite

        # Sinon, aucune action particulière vis-à-vis des fantômes
        return "N"

    def fantome_adjacent(self, pos: tuple[int, int], game_dict: dict) -> bool:
        """Retourne True si au moins un fantôme est adjacent (distance 1 en croix)."""
        x, y = pos
        positions_voisines = [(x, y-1), (x+1, y), (x, y+1), (x-1, y)]
        for fantome in game_dict.get("fantômes", []):
            fx, fy = fantome["position"]
            if (fx, fy) in positions_voisines:
                return True
        return False

    def fuir_fantomes(self, bomber_pos: tuple[int,int], game_dict: dict) -> str:
        """
        Retourne une direction pour fuir les fantômes trop proches (distance <= 2).
        Sinon, renvoie "N".
        """
        ghosts = self.get_nearby_ghosts(bomber_pos, game_dict)
        if ghosts and ghosts[0][0] <= 2:  # Si au moins un fantôme est à distance <= 2
            return self.get_safe_direction(bomber_pos, game_dict["bombes"], game_dict["map"])
        return "N"

    def est_case_proche_fantome(self, pos: tuple[int, int], game_dict: dict) -> bool:
        """
        Retourne True si la case 'pos' est occupée par un fantôme ou
        adjacente à un fantôme (distance 1).
        """
        x, y = pos
        for f in game_dict.get("fantômes", []):
            fx, fy = f["position"]
            if abs(x - fx) + abs(y - fy) <= 1:
                return True
        return False

    # -------------------------------------------------------------------------
    # 3) BOUCLE PRINCIPALE : DÉCISION PAR TOUR
    # -------------------------------------------------------------------------
    def action(self, game_dict: dict) -> str:
        """
        Méthode principale appelée à chaque tour par le moteur de jeu.
        Détermine l'action à réaliser : se déplacer, poser une bombe ou ne rien faire.
        """

        # 0) Récupérer la position du bomber
        bomber_pos = None
        for b in game_dict["bombers"]:
            if b["num_joueur"] == self.num_joueur:
                bomber_pos = b["position"]
                break
        if not bomber_pos:
            return "N"

        # 1) Calculer la liste des minerais à proximité
        minerais_proches = self.flood_fill(game_dict)

        # 2) Gérer la mémoire persistante
        self.derniere_action = getattr(self, "derniere_action", None)
        self.compte_recul = getattr(self, "compte_recul", 0)
        self.direction_recul = getattr(self, "direction_recul", None)
        self.derniere_bombe = getattr(self, "derniere_bombe", None)

        # 3) Vérifier le danger de bombes existantes
        if game_dict["bombes"]:
            danger = False
            for bomb in game_dict["bombes"]:
                if not self.get_safe_distance(bomb["position"], bomber_pos):
                    danger = True
                    break
            if danger:
                # Réduire le recul à 1 seul tour
                self.compte_recul = 1
                return self.get_safe_direction(bomber_pos, game_dict["bombes"], game_dict["map"])

        # 4) Gestion du recul après la pose d’une bombe
        if self.compte_recul > 0:
            self.compte_recul -= 1
            # Autoriser le déplacement sûr
            return self.get_safe_direction(bomber_pos, game_dict["bombes"], game_dict["map"])

        # 5) Gestion des fantômes
        ghost_decision = self.decide_ghost_action(bomber_pos, game_dict)
        if ghost_decision != "N":
            return ghost_decision

        # Vérifier si on doit fuir les fantômes avant de poser des bombes
        fuite_ghost = self.fuir_fantomes(bomber_pos, game_dict)
        if fuite_ghost != "N":
            return fuite_ghost

        # Détection d'un fantôme adjacent
        if self.fantome_adjacent(bomber_pos, game_dict):
            # Vérifier la sécurité avant de poser la bombe
            direction_fuite = self.get_safe_direction(bomber_pos, game_dict["bombes"], game_dict["map"])
            if direction_fuite != "N":
                self.en_fuite = True
                return "X"

        # 6) Si on n’a pas d’urgence fantôme, on poursuit la logique de minerais

        if not minerais_proches:
            return "N"

        # On cible le premier minerai (le plus proche)
        minerai_cible = minerais_proches[0][0]
        dx = abs(bomber_pos[0] - minerai_cible[0])
        dy = abs(bomber_pos[1] - minerai_cible[1])

        # Si le minerai est adjacent (même ligne/colonne à 1 case)
        # on tente de poser une bombe, en vérifiant qu'on peut fuir
        if ((dx <= 1 and dy == 0) or (dy <= 1 and dx == 0)):
            safe_dir = self.get_safe_direction(bomber_pos, game_dict["bombes"], game_dict["map"])
            if safe_dir != "N":
                self.derniere_bombe = bomber_pos
                self.compte_recul = 3
                return "X"

        # 7) Sinon, on se dirige vers le minerai
        direction = self.get_direction_to_target(bomber_pos, minerai_cible, game_dict)
        if direction != "N" and self.can_move_to(bomber_pos, direction, game_dict):
            pass
        else:
            # Si la direction calculée n'est pas possible, on tente d'autres directions
            for d in ["B","D","G","H"]:
                if self.can_move_to(bomber_pos, d, game_dict):
                    direction = d
                    break

        self.derniere_action = direction
        return direction