from pawpal_system import CareTask, Owner, Pet, ScheduleEntry, Scheduler


def test_mark_complete_changes_task_status() -> None:
    task = CareTask("Morning walk", "walk", 20, "high", due_time="08:00")

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_pet_task_count() -> None:
    pet = Pet("Mochi", "dog", 3)
    task = CareTask("Breakfast", "feeding", 10, "high", due_time="09:00")
    starting_count = len(pet.tasks)

    pet.add_task(task)

    assert len(pet.tasks) == starting_count + 1


def test_daily_task_completion_creates_next_occurrence() -> None:
    pet = Pet("Mochi", "dog", 3)
    task = CareTask(
        "Daily medication",
        "meds",
        5,
        "high",
        due_time="08:00",
        recurrence="daily",
        occurrence_date="2026-03-27",
    )
    pet.add_task(task)

    next_task = task.mark_complete(pet.tasks)

    assert task.completed is True
    assert next_task is not None
    assert next_task.title == "Daily medication"
    assert next_task.occurrence_date == "2026-03-28"
    assert len(pet.tasks) == 2


def test_detect_conflicts_returns_warning_for_overlapping_pet_tasks() -> None:
    owner = Owner("Jordan", 120)
    pet = Pet("Mochi", "dog", 3)
    scheduler = Scheduler(owner, pet, [])
    first_task = CareTask("Morning walk", "walk", 30, "high", due_time="08:00")
    second_task = CareTask("Breakfast", "feeding", 15, "high", due_time="08:15")
    entries = [
        ScheduleEntry(first_task, "08:00", "08:30"),
        ScheduleEntry(second_task, "08:15", "08:30"),
    ]

    warnings = scheduler.detect_conflicts(entries=entries)

    assert len(warnings) == 1
    assert "Mochi has overlapping tasks" in warnings[0]


def test_detect_conflicts_returns_warning_across_pets() -> None:
    owner = Owner("Jordan", 120)
    mochi = Pet("Mochi", "dog", 3)
    luna = Pet("Luna", "cat", 5)
    scheduler = Scheduler(owner, mochi, [])
    mochi_entries = [
        ScheduleEntry(CareTask("Morning walk", "walk", 30, "high"), "08:00", "08:30")
    ]
    luna_entries = [
        ScheduleEntry(CareTask("Medication", "meds", 10, "high"), "08:15", "08:25")
    ]

    warnings = scheduler.detect_conflicts(
        entries=mochi_entries,
        other_schedules=[(luna.name, luna_entries)],
    )

    assert len(warnings) == 1
    assert "overlaps with Luna task 'Medication'" in warnings[0]
