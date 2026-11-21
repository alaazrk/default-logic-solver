"""Fonctionnalité A : « Et si j'ajoute ce fait ? »

On calcule les extensions de la théorie (W, D) puis celles de (W + {fait}, D),
et on compare. Le but est de montrer la non-monotonie : ajouter un fait peut
RETIRER une conclusion (Tweety vole ; on ajoute « Pingouin -> ~Vole » et il ne vole plus).
"""
from dataclasses import dataclass, field
from typing import List

from .models import BaseDeConnaissance
from .parser import parser_formule
from .extensions import calculer_extensions
from .inference import litteraux
from .logic import est_coherent


@dataclass
class ComparaisonAjout:
    fait: str
    avant: List[List[str]]
    apres: List[List[str]]
    incoherent_apres: bool = False  # W + fait est incohérent

    # Littéraux connus (ex. 'v', '~p') selon la sémantique
    credules_avant: List[str] = field(default_factory=list)
    credules_apres: List[str] = field(default_factory=list)
    sceptiques_avant: List[str] = field(default_factory=list)
    sceptiques_apres: List[str] = field(default_factory=list)

    @property
    def credules_perdus(self):
        return sorted(set(self.credules_avant) - set(self.credules_apres))

    @property
    def credules_gagnes(self):
        return sorted(set(self.credules_apres) - set(self.credules_avant))

    @property
    def sceptiques_perdus(self):
        return sorted(set(self.sceptiques_avant) - set(self.sceptiques_apres))

    @property
    def sceptiques_gagnes(self):
        return sorted(set(self.sceptiques_apres) - set(self.sceptiques_avant))

    @property
    def non_monotone(self):
        """Vrai si l'ajout du fait a retiré au moins une conclusion."""
        return bool(self.credules_perdus or self.sceptiques_perdus)

    def en_texte(self) -> str:
        lignes = [f"Ajout du fait : {self.fait}", ""]
        lignes.append(f"Avant : {len(self.avant)} extension(s)")
        lignes.append(f"Après : {len(self.apres)} extension(s)")
        if self.incoherent_apres:
            lignes.append("⚠ Les faits deviennent incohérents : plus d'extension représentable.")
        lignes.append("")

        def ligne(titre, valeurs):
            return f"{titre} : {', '.join(valeurs) if valeurs else '—'}"

        lignes.append(ligne("Conclusions crédules perdues", self.credules_perdus))
        lignes.append(ligne("Conclusions crédules gagnées", self.credules_gagnes))
        lignes.append(ligne("Conclusions sceptiques perdues", self.sceptiques_perdus))
        lignes.append(ligne("Conclusions sceptiques gagnées", self.sceptiques_gagnes))
        lignes.append("")
        if self.non_monotone:
            lignes.append("→ Raisonnement NON monotone : ajouter ce fait a retiré des conclusions.")
        else:
            lignes.append("→ Aucune conclusion retirée par cet ajout.")
        return "\n".join(lignes)


def _litteraux_par_extension(extensions):
    return [set(litteraux(e)) for e in extensions]


def _credules_sceptiques(extensions):
    """(union, intersection) des littéraux des extensions."""
    if not extensions:
        return [], []
    ensembles = _litteraux_par_extension(extensions)
    return sorted(set.union(*ensembles)), sorted(set.intersection(*ensembles))


def comparer_ajout_fait(base: BaseDeConnaissance, nouveau_fait: str) -> ComparaisonAjout:
    """Compare les extensions de `base` avant et après l'ajout de `nouveau_fait`.
    Lève ValueError si le fait est mal écrit. La base d'origine n'est pas modifiée."""
    parser_formule(nouveau_fait)  # vérifie la syntaxe

    base_apres = BaseDeConnaissance(list(base.facts) + [nouveau_fait], list(base.defauts))

    avant = calculer_extensions(base)
    apres = calculer_extensions(base_apres)

    cred_av, scep_av = _credules_sceptiques(avant)
    cred_ap, scep_ap = _credules_sceptiques(apres)

    return ComparaisonAjout(
        fait=nouveau_fait,
        avant=avant,
        apres=apres,
        incoherent_apres=not est_coherent(base_apres.facts),
        credules_avant=cred_av,
        credules_apres=cred_ap,
        sceptiques_avant=scep_av,
        sceptiques_apres=scep_ap,
    )
