import math

MAX_CERCLES = 5   # au-delà, les cercles ne se chevauchent plus lisiblement


def intersection_litteraux(listes):
    """Littéraux présents dans toutes les extensions (= sceptiques)."""
    if not listes:
        return []
    return sorted(set.intersection(*(set(l) for l in listes)))


def regions_diagramme(listes):
    """{ensemble d'indices de cercles : [littéraux]} : dans quelle zone va chaque littéral."""
    regions = {}
    tous = set()
    for l in listes:
        tous |= set(l)
    for lit in sorted(tous):
        cle = frozenset(i for i, l in enumerate(listes) if lit in l)
        regions.setdefault(cle, []).append(lit)
    return regions


def _rapport_distance(n):
    """Distance centre du schéma / centre d'un cercle, en rayons.
    Assez grande pour que chaque cercle ait une zone à lui, assez petite
    pour que tous les cercles se recouvrent au milieu."""
    if n == 1:
        return 0.0
    if n == 2:
        return 0.6
    return min(0.95, max(0.6, 1.08 / (2 * math.sin(math.pi / n))))


def geometrie(n, largeur, hauteur, marge=40):
    """Renvoie (rayon, centres, etiquettes) pour n cercles dans un cadre largeur x hauteur.
    centres et etiquettes sont des listes de (x, y)."""
    cx, cy = largeur / 2, hauteur / 2
    rapport = _rapport_distance(n)
    rayon = (min(largeur, hauteur) / 2 - marge) / (1 + rapport)
    distance = rapport * rayon
    depart = math.pi if n == 2 else -math.pi / 2   # n=2 : gauche/droite ; sinon le 1er en haut
    centres, etiquettes = [], []
    for i in range(n):
        angle = depart + 2 * math.pi * i / n
        centres.append((cx + distance * math.cos(angle), cy + distance * math.sin(angle)))
        loin = distance + rayon + 16
        etiquettes.append((cx + loin * math.cos(angle), cy + loin * math.sin(angle)))
    return rayon, centres, etiquettes


def position_region(cle, centres, milieu, rayon):
    """Où écrire les littéraux d'une région (cle = indices des cercles qui la contiennent)."""
    mx, my = milieu
    pts = [centres[i] for i in cle]
    x = sum(p[0] for p in pts) / len(pts)
    y = sum(p[1] for p in pts) / len(pts)
    if len(cle) == len(centres):          # intersection de tous les cercles
        return mx, my
    # région partielle : on l'écarte un peu du milieu pour ne pas gêner l'intersection
    x, y = mx + (x - mx) * 1.2, my + (y - my) * 1.2
    if math.hypot(x - mx, y - my) < 0.15 * rayon:   # cas rare (cercles opposés) : on décale
        y = my + 0.4 * rayon
    return x, y
