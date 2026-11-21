"""Exemples prêts à charger (menu « Exemples » de l'interface).
Chaque exemple : des faits (W), des défauts (D) et ce qu'il faut observer."""

EXEMPLES = {
    "Tweety": {
        "faits": ["Oiseau"],
        "defauts": ["Oiseau : Vole / Vole"],
        "description": "Un seul défaut, qui s'applique : on attend 1 extension contenant Vole.",
    },
    "Pingouin": {
        "faits": ["Oiseau", "Pingouin", "Pingouin -> ~Vole"],
        "defauts": ["Oiseau : Vole / Vole"],
        "description": "Le défaut est bloqué : on attend 1 extension sans Vole (avec ~Vole).",
    },
    "Nixon": {
        "faits": ["Q", "R"],
        "defauts": ["Q : P / P", "R : ~P / ~P"],
        "description": "Deux défauts en conflit : 2 extensions. Essayez P : crédule oui, sceptique non.",
    },
    "Exemple du sujet": {
        "faits": ["o", "p -> o", "p -> ~v"],
        "defauts": ["o : v / v", "a : c / b"],
        "description": "1 extension, littéraux o, ~p, v. Le défaut d2 ne s'applique jamais (a n'est pas connu).",
    },
    "Sans extension": {
        "faits": [],
        "defauts": [" : ~p / p"],
        "description": "Aucune extension : le défaut contredit sa propre justification.",
    },
}