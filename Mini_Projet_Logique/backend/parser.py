import re
from sympy import Symbol, Equivalent,Implies 
from sympy.parsing.sympy_parser import parse_expr
from .models import RegleDeDefaut
from sympy.logic.inference import satisfiable, valid
def parser_formule(texte):

    # 1. Vérifier que la formule n'est pas vide
    if not texte or not texte.strip():
        raise ValueError("La formule est vide.")

    texte_propre = texte.strip()

    # 2. Transformer les prédicats en symboles atomiques
    symboles = {}

    def remplacer_predicat(match):
        nom = match.group(1)
        argument = match.group(2)

        nom_temporaire = f"PRED_{len(symboles)}"

        symboles[nom_temporaire] = Symbol(
            f"{nom}_{argument}"
        )

        return nom_temporaire

    texte_propre = re.sub(
        r"\b([A-Z]\w*)\s*\(\s*([a-z]\w*)\s*\)",
        remplacer_predicat,
        texte_propre
    )
    if re.search(r"\b(?!Equivalent\b)[A-Za-z_]\w*\s*\(", texte_propre):
        raise ValueError("Syntaxe de prédicat invalide : attendu Majuscule(minuscule), ex: P(x).")
    # 3. Transformer les opérateurs logiques
    texte_propre = texte_propre.replace("->", ">>")
    texte_propre = texte_propre.replace("→", ">>")
    texte_propre = texte_propre.replace("∧", "&")
    texte_propre = texte_propre.replace("^", "&")
    texte_propre = texte_propre.replace("∨", "|")
    texte_propre = texte_propre.replace("¬", "~")

    # 4. Traiter l'équivalence simple
    texte_propre = re.sub(
        r"\b(\w+)\s*↔\s*(\w+)\b",
        r"Equivalent(\1, \2)",
        texte_propre
    )
    for mot in re.findall(r"\b[A-Za-z_]\w*\b", texte_propre):
        if mot != "Equivalent" and mot not in symboles:
            symboles[mot] = Symbol(mot)

    symboles["Equivalent"] = Equivalent

    # 5. Convertir le texte en formule SymPy
    try:
        formule = parse_expr(
            texte_propre,
            local_dict=symboles
        )
        return formule

    except Exception as e:
        raise ValueError(
            f"Erreur de syntaxe dans la formule '{texte}' : {e}"
        )
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

    
    if prerequis:
        parser_formule(prerequis)
    parser_formule(conclusion)

    avertissements = []
    for j in justifications:
        formule_j = parser_formule(j)
        if satisfiable(formule_j) is False:
            avertissements.append(
                f"Avertissement : la justification '{j}' est incohérente (le défaut ne sera jamais applicable)."
            )

    return RegleDeDefaut(prerequis, justifications, conclusion), avertissements
