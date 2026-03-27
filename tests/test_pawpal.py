from pawpal_system import CareTask, Pet


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
