from sympy import And, Not
from sympy.logic.inference import satisfiable
from .parser import parser_formule


def est_satisfiable(f):
    return satisfiable(f) is not False


def est_valide(f):
    return satisfiable(Not(f)) is False


def est_coherent(formules_str: list[str]) -> bool:
    if not formules_str:
        return True

    formules_sympy = [parser_formule(f) for f in formules_str]
    conjonction = And(*formules_sympy)
    return est_satisfiable(conjonction)


def deduit(ensemble_str: list[str], cible_str: str) -> bool:
    if not cible_str or not cible_str.strip():
        return True

    cible = parser_formule(cible_str)

    if not ensemble_str:
        return est_valide(cible)

    formules_sympy = [parser_formule(f) for f in ensemble_str]
    test = And(*formules_sympy, Not(cible))
    return not est_satisfiable(test)


def est_consistant_avec(ensemble_str: list[str], justification_str: str) -> bool:
    return est_coherent(list(ensemble_str) + [justification_str])
