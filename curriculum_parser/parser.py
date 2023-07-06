import logging
import os
from typing import Generator
from pathlib import Path

import requests

from curriculum_parser.education_plan_discipline import EducationPlanDiscipline
from curriculum_parser.education_plan_file import EducationPlanFile

from ._pdf_parser import parse_pdf
from ._web_parser import get_plans
from .constants import EducationLevel

logger = logging.getLogger(__name__)


def _download_file(url: str, path: str):
    with open(path, "wb") as f:
        f.write(requests.get(url).content)


def get_plan_files() -> list[EducationPlanFile]:
    """Get all education plans from the site"""

    return get_plans()


def parse_plans(
    plan_files: list[EducationPlanFile],
) -> Generator[tuple[EducationPlanFile, list[EducationPlanDiscipline]], None, None]:
    """Parse specific education plans"""

    for plan_file in plan_files:
        try:
            # Because there is a different document format, we ignore it
            if (
                plan_file.education_level == EducationLevel.SECONDARY
                or plan_file.education_level == EducationLevel.POSTGRADUATE
            ):
                continue

            app_dir: Path = Path(__file__).parent
            plan_filename = plan_file.url.split("/")[-1]
            path = "pdf_files\\"
            path = os.path.join(app_dir, path)

            if not os.path.exists(path):
                os.makedirs(path)

            path = os.path.join(path, plan_filename)

            logger.info(
                f"Parsing {plan_filename}. Code: {plan_file.code}, name: {plan_file.name}"
            )

            _download_file(plan_file.url, path)

            # Parse file
            disciplines = parse_pdf(path)

            if disciplines is None:
                continue

            os.remove(path)

            yield plan_file, disciplines

        except Exception as e:
            logger.error(str(e))


def parse() -> (
    Generator[tuple[EducationPlanFile, list[EducationPlanDiscipline]], None, None]
):
    """Parse all education plans from the site"""
    plans = get_plans()

    yield from parse_plans(plans)
