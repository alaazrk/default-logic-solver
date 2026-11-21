from .logic import deduit
from .parser import parser_formule
def est_consequence_credule(extensions, formule_phi: str) -> bool:
    parser_formule(formule_phi)
    if not extensions:
        return False
    return any(deduit(ext, formule_phi) for ext in extensions)
def est_consequence_sceptique(extensions, formule_phi: str) -> bool:
    parser_formule(formule_phi)
    if not extensions:
        return False
    return all(deduit(ext, formule_phi) for ext in extensions)
