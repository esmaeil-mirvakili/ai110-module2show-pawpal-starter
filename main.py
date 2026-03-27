from datetime import date

from pawpal_system import CareTask, Owner, Pet, ScheduleEntry, Scheduler


def print_task_list(title: str, tasks: list[CareTask]) -> None:
    """Print a simple list of task titles and times."""
    print(title)
    if not tasks:
        print("  No matching tasks.")
        return

    for task in tasks:
        due_time = task.due_time or "no time"
        print(f"  - {task.title} at {due_time} [{task.priority}]")


def build_requested_entries(tasks: list[CareTask]) -> list[ScheduleEntry]:
    """Build schedule entries directly from requested due times."""
    requested_entries: list[ScheduleEntry] = []
    for task in tasks:
        if not task.due_time:
            continue
        start_hour, start_minute = map(int, task.due_time.split(":"))
        end_total_minutes = start_hour * 60 + start_minute + task.duration_minutes
        end_time = f"{end_total_minutes // 60:02d}:{end_total_minutes % 60:02d}"
        requested_entries.append(
            ScheduleEntry(task, task.due_time, end_time, reason="Requested time slot")
        )
    return requested_entries


def print_pet_schedule(owner: Owner, pet: Pet) -> None:
    """Print sorted task views and the generated schedule for one pet."""
    scheduler = Scheduler(owner, pet, pet.tasks)
    plan = scheduler.generate_plan()
    requested_entries = build_requested_entries(pet.tasks)
    warnings = scheduler.detect_conflicts(entries=requested_entries)

    print(f"\n{pet.name} ({pet.species})")
    print("-" * (len(pet.name) + len(pet.species) + 3))

    print_task_list("Tasks entered:", pet.tasks)
    print_task_list("Tasks sorted by time:", scheduler.sort_by_time())
    print_task_list("Open tasks:", scheduler.filter_tasks(completed=False))
    print_task_list("Completed tasks:", scheduler.filter_tasks(completed=True))
    print_task_list(f"Tasks for {pet.name}:", scheduler.filter_tasks(pet_name=pet.name))
    if warnings:
        print("Conflict warnings:")
        for warning in warnings:
            print(f"  {warning}")

    print("Generated schedule:")
    if not plan.selected_tasks:
        print("  No tasks scheduled.")
        return

    for entry in plan.selected_tasks:
        print(f"  {entry.format_for_display()}")


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

    # Add tasks out of chronological order to demonstrate sorting behavior.
    mochi.add_task(CareTask("Breakfast", "feeding", 10, "high", due_time="09:00"))
    mochi.add_task(CareTask("Medication", "meds", 15, "high", due_time="09:00"))
    mochi.add_task(CareTask("Evening walk", "walk", 25, "medium", due_time="18:00"))
    mochi.add_task(CareTask("Morning walk", "walk", 30, "high", due_time="08:00"))

    luna.add_task(CareTask("Laser play", "enrichment", 20, "medium", due_time="18:00"))
    luna.add_task(CareTask("Medication and meal", "meds", 15, "high", due_time="08:30"))
    luna.add_task(CareTask("Brush coat", "grooming", 10, "low", due_time="12:00"))

    # Mark one task complete so completion filtering has visible output.
    luna.tasks[2].mark_complete()

    print(f"Today's Schedule - {date.today().isoformat()}")
    print("=" * 30)
    print(f"Owner: {owner.name}")

    for pet in [mochi, luna]:
        print_pet_schedule(owner, pet)


if __name__ == "__main__":
    main()
