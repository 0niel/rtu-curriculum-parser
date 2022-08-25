from curriculum_parser import parser

if __name__ == "__main__":
    plans = parser.get_plan_files()
    for plan in plans:
        print(plan)
        print("\n")

    print("Count of plans:", len(plans))

    print("=" * 100)

    plan_to_parse = plans[0]

    for file, disciplines in parser.parse_plans([plan_to_parse]):
        print(file)
        print("\n")
        print(disciplines)
