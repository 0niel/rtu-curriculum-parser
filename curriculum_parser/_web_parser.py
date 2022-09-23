import re

import requests
from bs4 import BeautifulSoup, Tag

from .constants import EDUCATION_LEVELS_NAMES
from .education_plan_file import EducationPlanFile

requests.adapters.DEFAULT_RETRIES = 5


MIREA_URL = "https://www.mirea.ru"
MIREA_PLANS_URL = f"{MIREA_URL}/sveden/education/"

PLANS_TABLE_SELECTOR = "table[itemprop='eduOp']"


def _get_plans_table() -> Tag:
    response = requests.get(MIREA_PLANS_URL)

    if response.status_code != 200:
        raise Exception(
            f"Failed to get plans table. Status code: {response.status_code}"
        )

    soup = BeautifulSoup(response.text, "html.parser")
    return soup.select_one(PLANS_TABLE_SELECTOR)


def get_plans() -> list[EducationPlanFile]:
    plans_table = _get_plans_table()

    plans = []

    rows = plans_table.select("tr")
    # Skip first two rows (header and empty row)
    for row in rows[2:]:
        cells = row.select("td")
        if len(cells) < 5:
            continue

        code = cells[0].get_text().strip()

        # The name and if there is a profile, then it is in parentheses.
        # For example: Applied Mathematics and Computer Science
        # (Mathematical Modeling and Computational Mathematics)
        name = cells[1].text.strip()
        if "(" in name:
            name = name[: name.find("(")].strip()
            # Get value in ( ... ) with regex
            profile = re.search(r"\((.*)\)", cells[1].text.strip())[1].strip()

            if "«" in profile:
                # Get value in « ... » with regex
                profile = re.search(r"«(.*)»", profile)[1].strip()
        else:
            profile = None

        cell_val = cells[2].get_text()
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

        urls = cells[5].select("a")
        for url in urls:
            href = url.get("href")
            if href is None:
                continue
            if not href.endswith(".pdf"):
                continue

            href = MIREA_URL + href

            plans.append(
                EducationPlanFile(
                    url=href,
                    code=code,
                    name=name,
                    year=int(href.split("_")[-1].split(".")[0].strip()),
                    education_level=education_level,
                    profile=profile,
                )
            )

    return plans
