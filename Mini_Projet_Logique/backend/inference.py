from .logic import deduit
from .parser import parser_formule


def est_consequence_credule(extensions, formule_phi: str) -> bool:
    parser_formule(formule_phi)  # lève une erreur si la formule est mal écrite
    if not extensions:
        return False
    return any(deduit(ext, formule_phi) for ext in extensions)


def est_consequence_sceptique(extensions, formule_phi: str) -> bool:
    parser_formule(formule_phi)  # lève une erreur si la formule est mal écrite
    if not extensions:
        return False
    return all(deduit(ext, formule_phi) for ext in extensions)


def litteraux(extension):
    """Lettres dont la valeur est connue dans l'extension :
    'p' si p se déduit, '~p' si sa négation se déduit (utile pour l'affichage)."""
    noms = set()
    for formule in extension:
        noms |= {s.name for s in parser_formule(formule).free_symbols}

    resultat = []
    for nom in sorted(noms):
        if deduit(extension, nom):
            resultat.append(nom)
        elif deduit(extension, "~" + nom):
            resultat.append("~" + nom)
    return resultat