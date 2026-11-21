"""Étape 4 : sauvegarde et chargement d'une théorie (W, D) et de ses extensions.

Le fichier est un JSON lisible. On n'enregistre que des TEXTES (jamais d'objets
SymPy) : au chargement, on relit chaque texte avec le parseur, ce qui revérifie
au passage que le fichier est correct.

Exemple de fichier :
{
  "version": 1,
  "faits": ["o", "p -> o"],
  "defauts": ["o : v / v"],
  "extensions": [["o", "p -> o", "v"]]      <- ou null si pas encore calculées
}
"""
import json

from .models import BaseDeConnaissance
from .parser import parser_formule, parser_defaut

VERSION = 1


def base_depuis_textes(faits, defauts_txt):
    """Construit une BaseDeConnaissance à partir de textes, en vérifiant chacun.
    Lève ValueError (avec un message clair) si un texte est mal écrit."""
    for fait in faits:
        parser_formule(fait)
    defauts = [parser_defaut(d)[0] for d in defauts_txt]
    return BaseDeConnaissance(list(faits), defauts)


def sauvegarder(chemin, base, extensions=None):
    """Écrit la théorie dans un fichier JSON.
    extensions = None signifie « pas encore calculées »."""
    donnees = {
        "version": VERSION,
        "faits": list(base.facts),
        "defauts": [d.en_texte() for d in base.defauts],
        "extensions": None if extensions is None else [list(e) for e in extensions],
    }
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(donnees, f, ensure_ascii=False, indent=2)


def _liste_de_textes(valeur, nom):
    if not isinstance(valeur, list) or not all(isinstance(x, str) for x in valeur):
        raise ValueError(f"Fichier invalide : « {nom} » doit être une liste de textes.")
    return valeur


def charger(chemin):
    """Lit un fichier JSON. Renvoie (base, extensions).
    extensions vaut None si le fichier ne contient pas d'extensions.
    Lève OSError si le fichier est illisible, ValueError s'il est incorrect."""
    with open(chemin, "r", encoding="utf-8") as f:
        try:
            donnees = json.load(f)
        except json.JSONDecodeError:
            raise ValueError("Fichier invalide : ce n'est pas un JSON correct.") from None

    if not isinstance(donnees, dict):
        raise ValueError("Fichier invalide : le contenu doit être un objet JSON.")
    for cle in ("faits", "defauts"):
        if cle not in donnees:
            raise ValueError(f"Fichier invalide : la clé « {cle} » est absente.")

    faits = _liste_de_textes(donnees["faits"], "faits")
    defauts = _liste_de_textes(donnees["defauts"], "defauts")
    base = base_depuis_textes(faits, defauts)

    extensions = donnees.get("extensions")
    if extensions is not None:
        if not isinstance(extensions, list):
            raise ValueError("Fichier invalide : « extensions » doit être une liste.")
        for ext in extensions:
            for formule in _liste_de_textes(ext, "extensions"):
                parser_formule(formule)

    return base, extensions