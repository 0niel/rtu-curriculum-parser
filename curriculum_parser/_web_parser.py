from enum import IntEnum
import re

import requests
from bs4 import BeautifulSoup, Tag

from .constants import EDUCATION_LEVELS_NAMES
from .education_plan_file import EducationPlanFile

requests.adapters.DEFAULT_RETRIES = 5


MIREA_URL = "https://www.mirea.ru"
MIREA_PLANS_URL = MIREA_URL + "/sveden/education/"
CURRICULUM_TABLE_TITLE = "Информация об образовательной программе"


def _get_plans_table() -> Tag:
    response = requests.get(MIREA_PLANS_URL)

    if response.status_code != 200:
        raise Exception(
            f"Failed to get plans table. Status code: {response.status_code}"
        )

    soup = BeautifulSoup(response.text, "html.parser")

    return soup.find("p", text=CURRICULUM_TABLE_TITLE).find_next("table")


class _ColumnIndex(IntEnum):
    CODE = 0
    NAME = 1
    EDUCATION_LEVEL = 2
    PROFILE = 3

    URLS = 6


def get_plans() -> list[EducationPlanFile]:
    plans_table = _get_plans_table()

    plans = []

    rows = plans_table.select("tr")
    # Skip first two rows (header and empty row)
    for row in rows[2:]:
        cells = row.select("td")
        if len(cells) < 5:
            continue

        code = cells[_ColumnIndex.CODE].get_text().strip()

        name = cells[_ColumnIndex.NAME].text.strip()

        profile = cells[_ColumnIndex.PROFILE].text.strip()
        if "«" in profile:
            # Get value in « ... » with regex
            profile = re.search(r"«(.*)»", profile)[1].strip()

        cell_val = cells[_ColumnIndex.EDUCATION_LEVEL].get_text()
        education_level = next(
            (
                key
                for key, value in EDUCATION_LEVELS_NAMES.items()
                if value in cell_val.lower()
            ),
            None,
        )
        if education_level is None:
            continue

        urls = cells[_ColumnIndex.URLS].select("a")
        for url in urls:
            href = url.get("href")
            if href is None:
                continue
            if not href.endswith(".pdf"):
                continue

            href = MIREA_URL + href

            try:
                year = int(href.split("_")[-1].split(".")[0].strip())
            except ValueError:
                print(f"Failed to parse year from {href}")
                continue

            plans.append(
                EducationPlanFile(
                    url=href,
                    code=code,
                    name=name,
                    year=year,
                    education_level=education_level,
                    profile=profile,
                )
            )

    return plans
