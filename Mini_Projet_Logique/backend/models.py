from dataclasses import dataclass, field
from typing import List


@dataclass
class RegleDeDefaut:
  prerequis: str
  justifications: List[str]
  conclusion: str



@dataclass
class BaseDeConnaissance:
  facts: List[str] = field(default_factory=list)
  defauts: List[RegleDeDefaut] = field(default_factory=list)
