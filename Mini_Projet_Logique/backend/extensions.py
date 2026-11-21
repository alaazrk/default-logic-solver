from .logic import deduit, est_consistant_avec, est_coherent


def prerequis_satisfait(E, defaut):
    # un defaut sans prerequis est toujours applicable
    if not defaut.prerequis:
        return True
    return deduit(E, defaut.prerequis)


def justifications_valides(E, defaut):
    # verifie que chaque justification est coherente avec E
    for justification in defaut.justifications:
        if not est_consistant_avec(E, justification):
            return False
    return True


def defaut_applicable(E, defaut):
    return (
        prerequis_satisfait(E, defaut)
        and justifications_valides(E, defaut)
    )


def appliquer_defaut(E, defaut):
    nouvel_ensemble = E.copy()
    if defaut.conclusion not in nouvel_ensemble:
        nouvel_ensemble.append(defaut.conclusion)
    return nouvel_ensemble


def verifier_extension(E, defauts_appliques):
    # condition du point fixe : les justifications doivent rester valides dans E final
    for defaut in defauts_appliques:
        if not justifications_valides(E, defaut):
            return False
    return True


def sont_equivalents(E1, E2):
    # deux ensembles sont équivalents si chacun déduit toutes les formules de l'autre
    return all(deduit(E1, f) for f in E2) and all(deduit(E2, f) for f in E1)


def calculer_extensions(base):
    # Cas limite : si W est incohérent, la théorie de Reiter donne une extension
    # formée de TOUTES les formules. On ne sait pas la représenter : on renvoie [].
    if not est_coherent(base.facts):
        return []

    extensions = []
    etats_vus = set()  # ensembles de défauts déjà explorés
    E_initial = base.facts.copy()

    def deja_trouvee(E):
        return any(sont_equivalents(E, ext) for ext in extensions)

    def explorer(E, indices_appliques, defauts_appliques):
        # Le même ensemble de défauts appliqués donne le même E, quel que soit
        # l'ordre : inutile de l'explorer deux fois (on passe de n! à 2^n cas).
        cle = frozenset(indices_appliques)
        if cle in etats_vus:
            return
        etats_vus.add(cle)

        defauts_disponibles = []

        for i, defaut in enumerate(base.defauts):
            if i in indices_appliques:
                continue
            if defaut_applicable(E, defaut):
                defauts_disponibles.append((i, defaut))

        # si plus aucun defaut n'est applicable on valide et enregistre l'extension
        if not defauts_disponibles:
            if verifier_extension(E, defauts_appliques) and not deja_trouvee(E):
                extensions.append(E.copy())
            return

        # explorer chaque branche d'application possible
        for i, defaut in defauts_disponibles:
            nouvel_E = appliquer_defaut(E, defaut)

            nouveaux_indices = indices_appliques.copy()
            nouveaux_indices.add(i)

            nouveaux_defauts = defauts_appliques.copy()
            nouveaux_defauts.append(defaut)

            explorer(nouvel_E, nouveaux_indices, nouveaux_defauts)

    explorer(E_initial, set(), [])
    return extensions
