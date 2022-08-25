from dataclasses import dataclass
from typing import Optional

from .constants import ControlFormType


@dataclass
class EducationPlanDiscipline:
    name: str
    semester: int
    by_choice: bool  # По выбору
    is_optional: bool  # Факультативные
    is_practice: bool  # Практика
    control_forms: list[ControlFormType]
    lek: Optional[float] = None
    lab: Optional[float] = None
    pr: Optional[float] = None
    sr: Optional[float] = None
