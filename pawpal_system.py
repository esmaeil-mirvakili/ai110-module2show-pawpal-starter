from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Optional


PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}
RECURRENCE_OPTIONS = {"none", "daily", "weekly"}
DEFAULT_START_TIME = "08:00"


def _normalize_priority(priority: str) -> str:
    """Return a validated lowercase priority string."""
    normalized = priority.strip().lower()
    if normalized not in PRIORITY_RANK:
        raise ValueError("priority must be 'high', 'medium', or 'low'")
    return normalized


def _parse_time_to_minutes(time_str: str) -> int:
    """Convert an HH:MM time string into total minutes."""
    try:
        parsed = datetime.strptime(time_str, "%H:%M")
    except ValueError as exc:
        raise ValueError("time values must use HH:MM format") from exc
    return parsed.hour * 60 + parsed.minute


def _format_minutes(total_minutes: int) -> str:
    """Convert total minutes into an HH:MM time string."""
    hours, minutes = divmod(total_minutes, 60)
    return f"{hours:02d}:{minutes:02d}"


def _normalize_recurrence(recurrence: str) -> str:
    """Return a validated lowercase recurrence string."""
    normalized = recurrence.strip().lower()
    if normalized not in RECURRENCE_OPTIONS:
        raise ValueError("recurrence must be 'none', 'daily', or 'weekly'")
    return normalized


class Owner:
    def __init__(
        self,
        name: str,
        available_minutes: int,
        preferences: str = "",
        notes: str = "",
    ) -> None:
        if available_minutes < 0:
            raise ValueError("available_minutes must be non-negative")
        self.name = name
        self.available_minutes = available_minutes
        self.preferences = preferences
        self.notes = notes

    def update_preferences(self, preferences: str) -> None:
        """Update the owner's scheduling preferences."""
        self.preferences = preferences.strip()

    def set_available_time(self, available_minutes: int) -> None:
        """Set the number of minutes the owner has available."""
        if available_minutes < 0:
            raise ValueError("available_minutes must be non-negative")
        self.available_minutes = available_minutes

    def view_daily_plan(self, daily_plan: DailyPlan) -> str:
        """Return a readable summary of the provided daily plan."""
        return daily_plan.generate_summary()


class Pet:
    def __init__(
        self,
        name: str,
        species: str,
        age: int,
        health_notes: str = "",
        energy_level: str = "",
    ) -> None:
        if age < 0:
            raise ValueError("age must be non-negative")
        self.name = name
        self.species = species
        self.age = age
        self.health_notes = health_notes
        self.energy_level = energy_level
        self.tasks: list[CareTask] = []

    def add_health_note(self, note: str) -> None:
        """Append a new health note to the pet profile."""
        cleaned_note = note.strip()
        if not cleaned_note:
            return
        if self.health_notes:
            self.health_notes = f"{self.health_notes}; {cleaned_note}"
        else:
            self.health_notes = cleaned_note

    def update_profile(
        self,
        name: Optional[str] = None,
        species: Optional[str] = None,
        age: Optional[int] = None,
        energy_level: Optional[str] = None,
    ) -> None:
        """Update editable pet profile fields."""
        if name is not None:
            self.name = name
        if species is not None:
            self.species = species
        if age is not None:
            if age < 0:
                raise ValueError("age must be non-negative")
            self.age = age
        if energy_level is not None:
            self.energy_level = energy_level

    def get_care_summary(self) -> str:
        """Return a short summary of the pet's care profile."""
        summary = f"{self.name} is a {self.age}-year-old {self.species}"
        if self.energy_level:
            summary += f" with a {self.energy_level} energy level"
        if self.health_notes:
            summary += f". Health notes: {self.health_notes}"
        return summary + "."

    def add_task(self, task: CareTask) -> None:
        """Add a care task to this pet's task list."""
        self.tasks.append(task)


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
        recurrence: str = "none",
        occurrence_date: Optional[str] = None,
    ) -> None:
        if duration_minutes <= 0:
            raise ValueError("duration_minutes must be greater than zero")
        if due_time:
            _parse_time_to_minutes(due_time)
        if occurrence_date:
            date.fromisoformat(occurrence_date)
        self.title = title
        self.category = category
        self.duration_minutes = duration_minutes
        self.priority = _normalize_priority(priority)
        self.due_time = due_time
        self.is_required = is_required
        self.notes = notes
        self.recurrence = _normalize_recurrence(recurrence)
        self.occurrence_date = occurrence_date or date.today().isoformat()
        self.completed = False

    def mark_complete(self, task_list: Optional[list[CareTask]] = None) -> Optional[CareTask]:
        """Mark the task complete and create the next recurring task if needed."""
        self.completed = True
        next_task = self.create_next_occurrence()
        if next_task is not None and task_list is not None:
            task_list.append(next_task)
        return next_task

    def edit_task(
        self,
        title: Optional[str] = None,
        category: Optional[str] = None,
        duration_minutes: Optional[int] = None,
        priority: Optional[str] = None,
        due_time: Optional[str] = None,
        is_required: Optional[bool] = None,
        notes: Optional[str] = None,
        recurrence: Optional[str] = None,
        occurrence_date: Optional[str] = None,
    ) -> None:
        """Update any editable fields on the task."""
        if title is not None:
            self.title = title
        if category is not None:
            self.category = category
        if duration_minutes is not None:
            if duration_minutes <= 0:
                raise ValueError("duration_minutes must be greater than zero")
            self.duration_minutes = duration_minutes
        if priority is not None:
            self.priority = _normalize_priority(priority)
        if due_time is not None:
            if due_time:
                _parse_time_to_minutes(due_time)
            self.due_time = due_time
        if is_required is not None:
            self.is_required = is_required
        if notes is not None:
            self.notes = notes
        if recurrence is not None:
            self.recurrence = _normalize_recurrence(recurrence)
        if occurrence_date is not None:
            date.fromisoformat(occurrence_date)
            self.occurrence_date = occurrence_date

    def is_high_priority(self) -> bool:
        """Return whether the task has high priority."""
        return self.priority == "high"

    def fits_time_available(self, available_minutes: int) -> bool:
        """Return whether the task fits within the remaining time."""
        return self.duration_minutes <= available_minutes

    def create_next_occurrence(self) -> Optional[CareTask]:
        """Create the next task instance for daily or weekly recurring tasks."""
        if self.recurrence == "none":
            return None

        current_date = date.fromisoformat(self.occurrence_date)
        if self.recurrence == "daily":
            next_date = current_date + timedelta(days=1)
        else:
            next_date = current_date + timedelta(weeks=1)

        return CareTask(
            title=self.title,
            category=self.category,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            due_time=self.due_time,
            is_required=self.is_required,
            notes=self.notes,
            recurrence=self.recurrence,
            occurrence_date=next_date.isoformat(),
        )


class ScheduleEntry:
    def __init__(
        self,
        task: CareTask,
        start_time: str,
        end_time: str,
        reason: str = "",
    ) -> None:
        start_minutes = _parse_time_to_minutes(start_time)
        end_minutes = _parse_time_to_minutes(end_time)
        if end_minutes < start_minutes:
            raise ValueError("end_time must be after start_time")
        self.task = task
        self.start_time = start_time
        self.end_time = end_time
        self.reason = reason

    def format_for_display(self) -> str:
        """Return a human-readable schedule line for the entry."""
        return (
            f"{self.start_time}-{self.end_time}: {self.task.title} "
            f"({self.task.duration_minutes} min, {self.task.priority} priority)"
        )

    def overlaps_with(self, other: ScheduleEntry) -> bool:
        """Return whether this entry overlaps another entry."""
        this_start = _parse_time_to_minutes(self.start_time)
        this_end = _parse_time_to_minutes(self.end_time)
        other_start = _parse_time_to_minutes(other.start_time)
        other_end = _parse_time_to_minutes(other.end_time)
        return this_start < other_end and other_start < this_end


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
        if self.selected_tasks and total_minutes == 0:
            self.total_minutes = self.calculate_total_time()

    def add_task(self, schedule_entry: ScheduleEntry) -> None:
        """Add a scheduled entry to the daily plan."""
        self.selected_tasks.append(schedule_entry)
        if schedule_entry.reason:
            self.explanations.append(schedule_entry.reason)
        self.total_minutes = self.calculate_total_time()

    def remove_task(self, schedule_entry: ScheduleEntry) -> None:
        """Remove a scheduled entry from the daily plan."""
        self.selected_tasks.remove(schedule_entry)
        if schedule_entry.reason in self.explanations:
            self.explanations.remove(schedule_entry.reason)
        self.total_minutes = self.calculate_total_time()

    def calculate_total_time(self) -> int:
        """Recalculate and return the total scheduled minutes."""
        self.total_minutes = sum(entry.task.duration_minutes for entry in self.selected_tasks)
        return self.total_minutes

    def generate_summary(self) -> str:
        """Build a readable text summary of the daily plan."""
        scheduled = [entry.format_for_display() for entry in self.selected_tasks]
        lines = [f"Daily plan for {self.date}", f"Total scheduled time: {self.total_minutes} minutes"]
        if scheduled:
            lines.append("Scheduled tasks:")
            lines.extend(scheduled)
        else:
            lines.append("No tasks were scheduled.")

        if self.unscheduled_tasks:
            lines.append("Unscheduled tasks:")
            lines.extend(task.title for task in self.unscheduled_tasks)

        return "\n".join(lines)

    def explain_choices(self) -> list[str]:
        """Return the explanations for why tasks were scheduled."""
        if self.explanations:
            return self.explanations
        return [entry.reason for entry in self.selected_tasks if entry.reason]


class Scheduler:
    def __init__(
        self,
        owner: Owner,
        pet: Pet,
        all_tasks: Optional[list[CareTask]] = None,
        time_limit: int = 0,
        rules: str = "",
    ) -> None:
        if time_limit < 0:
            raise ValueError("time_limit must be non-negative")
        self.owner = owner
        self.pet = pet
        self.all_tasks = all_tasks or []
        self.time_limit = time_limit or owner.available_minutes
        self.rules = rules

    def generate_plan(self) -> DailyPlan:
        """Create a daily plan from the current owner, pet, and tasks."""
        selected_tasks, unscheduled_tasks = self.filter_tasks_by_constraints()
        entries = self.assign_times(selected_tasks)
        resolved_entries = self.resolve_conflicts(entries)

        explanations = [entry.reason for entry in resolved_entries if entry.reason]
        plan = DailyPlan(
            date=datetime.now().strftime("%Y-%m-%d"),
            selected_tasks=resolved_entries,
            explanations=explanations,
            unscheduled_tasks=unscheduled_tasks,
        )
        plan.calculate_total_time()
        return plan

    def sort_tasks_by_priority(self) -> list[CareTask]:
        """Return tasks ordered by required status, priority, and timing."""
        return sorted(
            self.all_tasks,
            key=lambda task: (
                not task.is_required,
                PRIORITY_RANK[task.priority],
                _parse_time_to_minutes(task.due_time) if task.due_time else 24 * 60,
                task.duration_minutes,
                task.title.lower(),
            ),
        )

    def sort_by_time(self, tasks: Optional[list[CareTask]] = None) -> list[CareTask]:
        """Return tasks ordered by due time, with untimed tasks last."""
        tasks_to_sort = self.all_tasks if tasks is None else tasks
        return sorted(
            tasks_to_sort,
            key=lambda task: (
                _parse_time_to_minutes(task.due_time) if task.due_time else 24 * 60,
                task.title.lower(),
            ),
        )

    def filter_tasks_by_constraints(self) -> tuple[list[CareTask], list[CareTask]]:
        """Return scheduled and unscheduled tasks based on the time limit."""
        remaining_minutes = self.time_limit
        selected_tasks: list[CareTask] = []
        unscheduled_tasks: list[CareTask] = []

        for task in self.sort_tasks_by_priority():
            if task.completed:
                continue
            if task.fits_time_available(remaining_minutes):
                selected_tasks.append(task)
                remaining_minutes -= task.duration_minutes
            else:
                unscheduled_tasks.append(task)

        return selected_tasks, unscheduled_tasks

    def filter_tasks(
        self,
        completed: Optional[bool] = None,
        pet_name: Optional[str] = None,
    ) -> list[CareTask]:
        """Return tasks filtered by completion status and optionally pet name."""
        if pet_name is not None and pet_name.strip().lower() != self.pet.name.strip().lower():
            return []

        filtered_tasks = self.all_tasks
        if completed is not None:
            filtered_tasks = [task for task in filtered_tasks if task.completed is completed]

        return filtered_tasks

    def complete_task(self, task: CareTask) -> Optional[CareTask]:
        """Mark a task complete and append its next recurring instance if needed."""
        return task.mark_complete(self.all_tasks)

    def assign_times(self, tasks: list[CareTask]) -> list[ScheduleEntry]:
        """Assign simple start and end times to selected tasks."""
        current_time = _parse_time_to_minutes(DEFAULT_START_TIME)
        entries: list[ScheduleEntry] = []

        for task in tasks:
            if task.due_time:
                due_minutes = _parse_time_to_minutes(task.due_time)
                start_minutes = max(current_time, due_minutes)
            else:
                start_minutes = current_time

            end_minutes = start_minutes + task.duration_minutes
            reason = self._build_reason(task)
            entries.append(
                ScheduleEntry(
                    task=task,
                    start_time=_format_minutes(start_minutes),
                    end_time=_format_minutes(end_minutes),
                    reason=reason,
                )
            )
            current_time = end_minutes

        return entries

    def resolve_conflicts(self, entries: list[ScheduleEntry]) -> list[ScheduleEntry]:
        """Shift overlapping entries so the final schedule is sequential."""
        if not entries:
            return []

        ordered_entries = sorted(entries, key=lambda entry: _parse_time_to_minutes(entry.start_time))
        resolved_entries: list[ScheduleEntry] = [ordered_entries[0]]

        for entry in ordered_entries[1:]:
            previous = resolved_entries[-1]
            previous_end = _parse_time_to_minutes(previous.end_time)
            entry_start = _parse_time_to_minutes(entry.start_time)

            if entry_start < previous_end:
                entry_start = previous_end

            entry_end = entry_start + entry.task.duration_minutes
            resolved_entries.append(
                ScheduleEntry(
                    task=entry.task,
                    start_time=_format_minutes(entry_start),
                    end_time=_format_minutes(entry_end),
                    reason=entry.reason,
                )
            )

        return resolved_entries

    def detect_conflicts(
        self,
        entries: Optional[list[ScheduleEntry]] = None,
        other_schedules: Optional[list[tuple[str, list[ScheduleEntry]]]] = None,
    ) -> list[str]:
        """Return warning messages for overlapping tasks in one or more schedules."""
        local_entries = entries if entries is not None else self.generate_plan().selected_tasks
        warnings: list[str] = []

        for index, entry in enumerate(local_entries):
            for other_entry in local_entries[index + 1 :]:
                if entry.overlaps_with(other_entry):
                    overlap_start, overlap_end = self._overlap_window(entry, other_entry)
                    warnings.append(
                        f"Warning: {self.pet.name} has overlapping tasks "
                        f"'{entry.task.title}' and '{other_entry.task.title}' "
                        f"from {overlap_start} to {overlap_end}."
                    )

        if other_schedules is None:
            return warnings

        for other_pet_name, other_entries in other_schedules:
            for entry in local_entries:
                for other_entry in other_entries:
                    if entry.overlaps_with(other_entry):
                        overlap_start, overlap_end = self._overlap_window(entry, other_entry)
                        warnings.append(
                            f"Warning: {self.pet.name} task '{entry.task.title}' overlaps with "
                            f"{other_pet_name} task '{other_entry.task.title}' "
                            f"from {overlap_start} to {overlap_end}."
                        )

        return warnings

    def _build_reason(self, task: CareTask) -> str:
        """Build a plain-language explanation for selecting a task."""
        reasons = []
        if task.is_required:
            reasons.append("required")
        reasons.append(f"{task.priority} priority")
        if task.due_time:
            reasons.append(f"scheduled around {task.due_time}")

        preferences = self.owner.preferences.lower()
        if preferences and (
            task.category.lower() in preferences or task.title.lower() in preferences
        ):
            reasons.append("matches owner preference")

        return f"{task.title} was selected because it is " + ", ".join(reasons) + "."

    def _overlap_window(self, first: ScheduleEntry, second: ScheduleEntry) -> tuple[str, str]:
        """Return the shared time window for two overlapping schedule entries."""
        overlap_start = max(
            _parse_time_to_minutes(first.start_time),
            _parse_time_to_minutes(second.start_time),
        )
        overlap_end = min(
            _parse_time_to_minutes(first.end_time),
            _parse_time_to_minutes(second.end_time),
        )
        return _format_minutes(overlap_start), _format_minutes(overlap_end)
