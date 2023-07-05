from curriculum_parser import parser
import concurrent.futures
import os
from multiprocessing import Process
from pathlib import Path
import requests
from models.control_form import ControlForm
from models.discipline import Discipline
from models.discipline_name import DisciplineName
from models.education_direction import EducationDirection
from models.education_plan import EducationPlan
from curriculum_parser.constants import EducationLevel
from curriculum_parser.education_plan_file import EducationPlanFile
from curriculum_parser.parser import parse_pdf
import sqlite3

app_dir: Path = Path(__file__).parent


def parse_plan(plan: EducationPlanFile):
    try:
        if plan.education_level in [
            EducationLevel.SECONDARY,
            EducationLevel.POSTGRADUATE,
        ]:
            return

        plan_filename = plan.url.split("/")[-1]
        path = "pdf_files\\"
        path = os.path.join(app_dir, path)

        if not os.path.exists(path):
            os.makedirs(path)

        path = os.path.join(path, plan_filename)
        print("Parsing plan: ", plan_filename)
        print("Code: ", plan.code, " / Name: ", plan.name)

        with open(path, "wb") as f:
            f.write(requests.get(plan.url).content)

        # Parse file
        print("Parsing pdf...")
        print("Path: ", path)
        disciplines = parse_pdf(path)

        print("Count of disciplines: ", len(disciplines))

        return plan, disciplines

    except Exception as e:
        print(e)


def save_curriculum_to_db(plan, disciplines):
    discipline_objs = []

    # Save to database
    for discipline in disciplines:
        # Save to database
        discipline_name = DisciplineName.get_or_create(discipline.name)

        control_forms = [
            ControlForm.get_or_create(control_form.value)
            for control_form in discipline.control_forms
        ]

        # Save to database
        discipline_obj = Discipline.get_or_create(
            discipline_name.id,
            discipline.semester,
            discipline.by_choice,
            discipline.is_optional,
            discipline.is_practice,
            discipline.lek,
            discipline.lab,
            discipline.pr,
            discipline.sr,
            control_forms,
        )

        discipline_objs.append(discipline_obj)

        education_direction = EducationDirection.get_or_create(plan.name, plan.code)

        # Save to database
        EducationPlan.get_or_create(
            plan.profile,
            education_direction.id,
            plan.year,
            plan.education_level.value,
            discipline_objs,
        )


def parse():
    plans = parser.get_plan_files()

    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
        futures = [executor.submit(parse_plan, plan) for plan in plans]
        for future in concurrent.futures.as_completed(futures):
            try:
                plan, disciplines = future.result()
                save_curriculum_to_db(plan, disciplines)
            except Exception as e:
                print("=============================")
                print(e)
                print("=============================")
                print()


if __name__ == "__main__":
    parse()

    # Открываем plans.db и plans_new.db
    conn = sqlite3.connect("plans.db")
    conn_new = sqlite3.connect("plans_new.db")

    cursor = conn.cursor()
    cursor_new = conn_new.cursor()

    # Получаем profile, year, и по education_direction_id с помощью INNER JOIN education_directions.code, education_directions.name
    cursor_new.execute(
        """
        SELECT profile, year, education_direction_id, education_directions.code, education_directions.name
        FROM education_plans
        INNER JOIN education_directions
        ON education_plans.education_direction_id = education_directions.id
        """
    )

    # Получаем то же самое из старой базы
    cursor.execute(
        """
        SELECT profile, year, education_direction_id, education_directions.code, education_directions.name
        FROM education_plans
        INNER JOIN education_directions
        ON education_plans.education_direction_id = education_directions.id
        """
    )

    new_db_data = cursor_new.fetchall()
    old_db_data = cursor.fetchall()

    print("Количество планов в новой базе: ", len(new_db_data))
    print("Количество планов в старой базе: ", len(old_db_data))
    print("Всего новых планов: ", len(new_db_data) - len(old_db_data))

    for_compare_old = [[plan[0], plan[1], plan[3], plan[4]] for plan in old_db_data]
    for_compare_new = [[plan[0], plan[1], plan[3], plan[4]] for plan in new_db_data]

    # Новые планы:
    print("Новые планы:")
    new_plans = [plan for plan in for_compare_new if plan not in for_compare_old]
    for plan in new_plans:
        print(
            f"Профиль: {plan[0]}, Год: {plan[1]}, Код: {plan[2]}, Направление: {plan[3]}"
        )

    # Удаленные планы:

    print("\n\nУдаленные планы:")
    deleted_plans = [plan for plan in for_compare_old if plan not in for_compare_new]
    for plan in deleted_plans:
        print(
            f"Профиль: {plan[0]}, Год: {plan[1]}, Код: {plan[2]}, Направление: {plan[3]}"
        )
