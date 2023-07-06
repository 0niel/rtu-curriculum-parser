from dataclasses import dataclass
from typing import Optional

from .constants import EducationLevel


@dataclass
class EducationPlanFile:
    url: str
    code: str
    name: str
    year: int
    education_level: EducationLevel
    annot_url: Optional[str] = None
    profile: Optional[str] = None
