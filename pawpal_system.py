from __future__ import annotations

from typing import Optional


class Owner:
    def __init__(
        self,
        name: str,
        available_minutes: int,
        preferences: str = "",
        notes: str = "",
    ) -> None:
        self.name = name
        self.available_minutes = available_minutes
        self.preferences = preferences
        self.notes = notes

    def update_preferences(self, preferences: str) -> None:
        pass

    def set_available_time(self, available_minutes: int) -> None:
        pass

    def view_daily_plan(self, daily_plan: DailyPlan) -> None:
        pass


class Pet:
    def __init__(
        self,
        name: str,
        species: str,
        age: int,
        health_notes: str = "",
        energy_level: str = "",
    ) -> None:
        self.name = name
        self.species = species
        self.age = age
        self.health_notes = health_notes
        self.energy_level = energy_level

    def add_health_note(self, note: str) -> None:
        pass

    def update_profile(
        self,
        name: Optional[str] = None,
        species: Optional[str] = None,
        age: Optional[int] = None,
        energy_level: Optional[str] = None,
    ) -> None:
        pass

    def get_care_summary(self) -> str:
        pass


class CareTask:
    def __init__(
        self,
        title: str,
        category: str,
        duration_minutes: int,
        priority: str,
        due_time: str = "",
        is_required: bool = True,
        notes: str = "",
    ) -> None:
        self.title = title
        self.category = category
        self.duration_minutes = duration_minutes
        self.priority = priority
        self.due_time = due_time
        self.is_required = is_required
        self.notes = notes

    def mark_complete(self) -> None:
        pass

    def edit_task(
        self,
        title: Optional[str] = None,
        category: Optional[str] = None,
        duration_minutes: Optional[int] = None,
        priority: Optional[str] = None,
        due_time: Optional[str] = None,
        is_required: Optional[bool] = None,
        notes: Optional[str] = None,
    ) -> None:
        pass

    def is_high_priority(self) -> bool:
        pass

    def fits_time_available(self, available_minutes: int) -> bool:
        pass


class ScheduleEntry:
    def __init__(
        self,
        task: CareTask,
        start_time: str,
        end_time: str,
        reason: str = "",
    ) -> None:
        self.task = task
        self.start_time = start_time
        self.end_time = end_time
        self.reason = reason

    def format_for_display(self) -> str:
        pass

    def overlaps_with(self, other: ScheduleEntry) -> bool:
        pass


class DailyPlan:
    def __init__(
        self,
        date: str,
        selected_tasks: Optional[list[ScheduleEntry]] = None,
        total_minutes: int = 0,
        explanations: Optional[list[str]] = None,
        unscheduled_tasks: Optional[list[CareTask]] = None,
    ) -> None:
        self.date = date
        self.selected_tasks = selected_tasks or []
        self.total_minutes = total_minutes
        self.explanations = explanations or []
        self.unscheduled_tasks = unscheduled_tasks or []

    def add_task(self, schedule_entry: ScheduleEntry) -> None:
        pass

    def remove_task(self, schedule_entry: ScheduleEntry) -> None:
        pass

    def calculate_total_time(self) -> int:
        pass

    def generate_summary(self) -> str:
        pass

    def explain_choices(self) -> list[str]:
        pass


class Scheduler:
    def __init__(
        self,
        owner: Owner,
        pet: Pet,
        all_tasks: Optional[list[CareTask]] = None,
        time_limit: int = 0,
        rules: str = "",
    ) -> None:
        self.owner = owner
        self.pet = pet
        self.all_tasks = all_tasks or []
        self.time_limit = time_limit
        self.rules = rules

    def generate_plan(self) -> DailyPlan:
        pass

    def sort_tasks_by_priority(self) -> list[CareTask]:
        pass

    def filter_tasks_by_constraints(self) -> list[CareTask]:
        pass

    def assign_times(self, tasks: list[CareTask]) -> list[ScheduleEntry]:
        pass

    def resolve_conflicts(self, entries: list[ScheduleEntry]) -> list[ScheduleEntry]:
        pass
