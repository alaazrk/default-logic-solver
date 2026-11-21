from dataclasses import dataclass, field
from typing import List


@dataclass
class RegleDeDefaut:
    """Un défaut  prerequis : just1, just2 / conclusion  (tout en texte)."""
    prerequis: str
    justifications: List[str]
    conclusion: str

    def en_texte(self) -> str:
        """Réécrit le défaut sous la forme saisie par l'utilisateur."""
        return f"{self.prerequis} : {', '.join(self.justifications)} / {self.conclusion}"


@dataclass
class BaseDeConnaissance:
    """La théorie (W, D) : les faits certains et les défauts."""
    facts: List[str] = field(default_factory=list)
    defauts: List[RegleDeDefaut] = field(default_factory=list)