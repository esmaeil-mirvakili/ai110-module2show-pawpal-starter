from datetime import date

from pawpal_system import CareTask, Owner, Pet, Scheduler


def print_pet_schedule(owner: Owner, pet: Pet, tasks: list[CareTask]) -> None:
    scheduler = Scheduler(owner, pet, tasks)
    plan = scheduler.generate_plan()

    print(f"\n{pet.name} ({pet.species})")
    print("-" * (len(pet.name) + len(pet.species) + 3))

    if not plan.selected_tasks:
        print("No tasks scheduled.")
        return

    for entry in plan.selected_tasks:
        print(entry.format_for_display())


def main() -> None:
    owner = Owner(
        name="Jordan",
        available_minutes=120,
        preferences="morning walk, breakfast, evening walk",
        notes="Prefers the highest-priority care tasks first.",
    )

    mochi = Pet(
        name="Mochi",
        species="dog",
        age=3,
        energy_level="high",
        health_notes="Needs daily exercise.",
    )
    luna = Pet(
        name="Luna",
        species="cat",
        age=5,
        energy_level="medium",
        health_notes="Needs medication with food.",
    )

    pet_tasks = {
        mochi: [
            CareTask("Morning walk", "walk", 30, "high", due_time="08:00"),
            CareTask("Breakfast", "feeding", 10, "high", due_time="09:00"),
        ],
        luna: [
            CareTask("Medication and meal", "meds", 15, "high", due_time="08:30"),
            CareTask("Laser play", "enrichment", 20, "medium", due_time="18:00"),
        ],
    }

    print(f"Today's Schedule - {date.today().isoformat()}")
    print("=" * 30)
    print(f"Owner: {owner.name}")

    for pet, tasks in pet_tasks.items():
        print_pet_schedule(owner, pet, tasks)


if __name__ == "__main__":
    main()
