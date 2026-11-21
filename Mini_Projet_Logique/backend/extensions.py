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
    # condition du point fixe les justifications doivent rester valides dans E final
    for defaut in defauts_appliques:
        if not justifications_valides(E, defaut):
            return False
    return True


def calculer_extensions(base):
    if not est_coherent(base.facts):
        return []

    extensions = []
    signatures_vues = set()
    E_initial = base.facts.copy()

    def explorer(E, indices_appliques, defauts_appliques):
        defauts_disponibles = []

        for i, defaut in enumerate(base.defauts):
            if i in indices_appliques:
                continue
            if defaut_applicable(E, defaut):
                defauts_disponibles.append((i, defaut))

        # si plus aucun defaut nest applicable on valide et enregistre lextension
        if not defauts_disponibles:
            if verifier_extension(E, defauts_appliques):
                signature = frozenset(E)
                if signature not in signatures_vues:
                    signatures_vues.add(signature)
                    extensions.append(E.copy())
            return

        # explorer chaque branche d'application possible
        for i, defaut in defauts_disponibles:
            nouvel_E = appliquer_defaut(E, defaut)

            nouveaux_indices = indices_appliques.copy()
            nouveaux_indices.add(i)

            nouveaux_defauts = defauts_appliques.copy()
            nouveaux_defauts.append(defaut)

            explorer(
                nouvel_E,
                nouveaux_indices,
                nouveaux_defauts
            )

    explorer(E_initial, set(), [])
    return extensions
