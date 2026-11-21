import re
from functools import lru_cache

from sympy import Symbol, And, Or, Not, Implies, Equivalent
from sympy.logic.inference import satisfiable

from .models import RegleDeDefaut


# 1) Découpage du texte en "jetons" (symboles, opérateurs, parenthèses)

# L'ordre compte : "<->" doit être testé avant "->".
MOTIF_JETON = re.compile(r"\s*(<->|↔|->|→|∧|∨|¬|\^|&|\||~|\(|\)|[A-Za-z_]\w*)")

# Plusieurs écritures possibles pour un même opérateur : on les unifie.
NORMALISE = {"↔": "<->", "→": "->", "∧": "&", "^": "&", "∨": "|", "¬": "~"}

MOT = re.compile(r"[A-Za-z_]\w*")


def _decouper(texte):
    jetons = []
    pos = 0
    texte = texte.rstrip()
    while pos < len(texte):
        m = MOTIF_JETON.match(texte, pos)
        if not m:
            caractere = texte[pos:].strip()[0]
            raise ValueError(f"caractère inattendu : '{caractere}'")
        jetons.append(NORMALISE.get(m.group(1), m.group(1)))
        pos = m.end()
    return jetons



# 2) Analyseur : un niveau de priorité = une fonction
#    (du moins prioritaire au plus prioritaire)
#    <->   puis   ->   puis   |   puis   &   puis   ~   puis   atome

class _Analyseur:
    def __init__(self, jetons):
        self.jetons = jetons
        self.i = 0

    def courant(self):
        return self.jetons[self.i] if self.i < len(self.jetons) else None

    def avancer(self):
        jeton = self.courant()
        self.i += 1
        return jeton

    def equivalence(self):
        gauche = self.implication()
        while self.courant() == "<->":
            self.avancer()
            gauche = Equivalent(gauche, self.implication())
        return gauche

    def implication(self):
        gauche = self.disjonction()
        if self.courant() == "->":
            self.avancer()
            return Implies(gauche, self.implication())  # a -> b -> c = a -> (b -> c)
        return gauche

    def disjonction(self):
        termes = [self.conjonction()]
        while self.courant() == "|":
            self.avancer()
            termes.append(self.conjonction())
        return Or(*termes) if len(termes) > 1 else termes[0]

    def conjonction(self):
        termes = [self.negation()]
        while self.courant() == "&":
            self.avancer()
            termes.append(self.negation())
        return And(*termes) if len(termes) > 1 else termes[0]

    def negation(self):
        if self.courant() == "~":
            self.avancer()
            return Not(self.negation())
        return self.atome()

    def atome(self):
        jeton = self.courant()
        if jeton is None:
            raise ValueError("formule incomplète, il manque un élément à la fin")

        if jeton == "(":
            self.avancer()
            formule = self.equivalence()
            if self.courant() != ")":
                raise ValueError("parenthèse fermante manquante")
            self.avancer()
            return formule

        if MOT.fullmatch(jeton):
            self.avancer()
            if self.courant() == "(":  # prédicat de la forme P(x)
                return self.predicat(jeton)
            return Symbol(jeton)  # Symbol(...) évite les noms réservés de SymPy (Q, S, N, E, I, O)

        raise ValueError(f"élément inattendu : '{jeton}'")

    def predicat(self, nom):
        erreur = "syntaxe de prédicat invalide : attendu Majuscule(minuscule), ex. P(x)"
        self.avancer()  # la parenthèse ouvrante
        argument = self.avancer()
        if not nom[0].isupper() or argument is None or not MOT.fullmatch(argument) \
                or not argument[0].islower() or self.avancer() != ")":
            raise ValueError(erreur)
        return Symbol(f"{nom}_{argument}")  # P(karim) devient la lettre P_karim



# 3) Fonctions utilisées par le reste du projet

@lru_cache(maxsize=None)  # on mémorise : un même texte n'est analysé qu'une fois
def parser_formule(texte):
    if not texte or not texte.strip():
        raise ValueError("La formule est vide.")
    try:
        analyseur = _Analyseur(_decouper(texte))
        formule = analyseur.equivalence()
        if analyseur.courant() is not None:
            raise ValueError(f"élément inattendu : '{analyseur.courant()}'")
        return formule
    except ValueError as e:
        raise ValueError(f"Erreur dans la formule '{texte}' : {e}") from None


def parser_defaut(texte):
    if not texte or not texte.strip():
        raise ValueError("Le défaut est vide.")

    if texte.count(":") != 1 or texte.count("/") != 1:
        raise ValueError("Le défaut doit contenir exactement un ':' et un '/'.")

    if texte.index(":") > texte.index("/"):
        raise ValueError("Format attendu : prérequis : just1, just2 / conséquent.")

    prerequis, reste = [x.strip() for x in texte.split(":", 1)]
    justifs_txt, conclusion = [x.strip() for x in reste.split("/", 1)]

    if not conclusion:
        raise ValueError("Le conséquent est vide.")
    if not justifs_txt:
        raise ValueError("Il faut au moins une justification.")

    justifications = [j.strip() for j in justifs_txt.split(",")]
    if any(not j for j in justifications):
        raise ValueError("Une justification est vide.")

    if prerequis:  # un prérequis vide est permis (toujours vrai)
        parser_formule(prerequis)
    parser_formule(conclusion)

    avertissements = []
    for j in justifications:
        if satisfiable(parser_formule(j)) is False:
            avertissements.append(
                f"Avertissement : la justification '{j}' est incohérente "
                "(le défaut ne sera jamais applicable)."
            )

    return RegleDeDefaut(prerequis, justifications, conclusion), avertissements