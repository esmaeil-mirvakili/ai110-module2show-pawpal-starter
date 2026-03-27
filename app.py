from datetime import time

import streamlit as st

from pawpal_system import CareTask, Owner, Pet, ScheduleEntry, Scheduler


def initialize_state() -> None:
    """Create default owner, pet, and plan objects in session state."""
    if "owner" not in st.session_state:
        st.session_state.owner = Owner(
            name="Jordan",
            available_minutes=90,
            preferences="morning walk",
        )
    if "pet" not in st.session_state:
        st.session_state.pet = Pet(
            name="Mochi",
            species="dog",
            age=3,
            energy_level="high",
        )
    if "daily_plan" not in st.session_state:
        st.session_state.daily_plan = None


def sync_profiles(
    owner_name: str,
    available_minutes: int,
    preferences: str,
    pet_name: str,
    species: str,
    age: int,
    energy_level: str,
    health_notes: str,
) -> None:
    """Update the session owner and pet from the current UI values."""
    owner = st.session_state.owner
    owner.name = owner_name.strip() or owner.name
    owner.set_available_time(int(available_minutes))
    owner.update_preferences(preferences)

    pet = st.session_state.pet
    pet.update_profile(
        name=pet_name.strip() or pet.name,
        species=species,
        age=int(age),
        energy_level=energy_level,
    )
    pet.health_notes = health_notes.strip()


def task_rows(tasks: list[CareTask]) -> list[dict[str, object]]:
    """Convert task objects into rows for display."""
    return [
        {
            "title": task.title,
            "category": task.category,
            "duration_minutes": task.duration_minutes,
            "priority": task.priority,
            "due_time": task.due_time,
            "required": task.is_required,
            "completed": task.completed,
            "recurrence": task.recurrence,
        }
        for task in tasks
    ]


def schedule_rows(plan_entries: list[ScheduleEntry]) -> list[dict[str, object]]:
    """Convert scheduled entries into rows for display."""
    return [
        {
            "start_time": entry.start_time,
            "end_time": entry.end_time,
            "task": entry.task.title,
            "category": entry.task.category,
            "priority": entry.task.priority,
            "reason": entry.reason,
        }
        for entry in plan_entries
    ]


def build_requested_entries(tasks: list[CareTask]) -> list[ScheduleEntry]:
    """Build entries from requested task times for conflict checks."""
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

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

initialize_state()

st.title("🐾 PawPal+")

st.markdown(
    """
PawPal+ helps a pet owner organize care tasks for the day.
This version connects the Streamlit UI to the scheduling classes in `pawpal_system.py`.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet based on constraints like time, priority, and preferences.
"""
    )

st.divider()

st.subheader("Owner and Pet")
owner = st.session_state.owner
pet = st.session_state.pet

owner_name = st.text_input("Owner name", value=owner.name)
available_minutes = st.number_input(
    "Available time today (minutes)",
    min_value=0,
    max_value=720,
    value=owner.available_minutes,
)
preferences = st.text_input("Owner preferences", value=owner.preferences)

pet_name = st.text_input("Pet name", value=pet.name)
species = st.selectbox(
    "Species",
    ["dog", "cat", "other"],
    index=["dog", "cat", "other"].index(pet.species) if pet.species in ["dog", "cat", "other"] else 2,
)
age = st.number_input("Pet age", min_value=0, max_value=40, value=pet.age)
energy_level = st.selectbox(
    "Energy level",
    ["low", "medium", "high"],
    index=["low", "medium", "high"].index(pet.energy_level) if pet.energy_level in ["low", "medium", "high"] else 1,
)
health_notes = st.text_input("Health notes", value=pet.health_notes)

if st.button("Save pet profile"):
    sync_profiles(
        owner_name,
        int(available_minutes),
        preferences,
        pet_name,
        species,
        int(age),
        energy_level,
        health_notes,
    )
    st.success("Owner and pet profile saved.")

st.caption(st.session_state.pet.get_care_summary())

st.divider()

st.subheader("Tasks")
task_title = st.text_input("Task title", value="Morning walk")

col1, col2, col3 = st.columns(3)
with col1:
    category = st.selectbox("Category", ["walk", "feeding", "meds", "grooming", "enrichment"])
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

col4, col5 = st.columns(2)
with col4:
    due_time = st.time_input("Preferred time", value=time(8, 0))
with col5:
    is_required = st.checkbox("Required today", value=True)

task_notes = st.text_input("Task notes", value="")

if st.button("Add task"):
    sync_profiles(
        owner_name,
        int(available_minutes),
        preferences,
        pet_name,
        species,
        int(age),
        energy_level,
        health_notes,
    )
    try:
        task = CareTask(
            title=task_title,
            category=category,
            duration_minutes=int(duration),
            priority=priority,
            due_time=due_time.strftime("%H:%M"),
            is_required=is_required,
            notes=task_notes,
        )
        st.session_state.pet.add_task(task)
        st.session_state.daily_plan = None
        st.success(f"Added task for {st.session_state.pet.name}: {task.title}")
    except ValueError as exc:
        st.error(str(exc))

if st.session_state.pet.tasks:
    scheduler = Scheduler(
        st.session_state.owner,
        st.session_state.pet,
        st.session_state.pet.tasks,
    )
    requested_entries = build_requested_entries(st.session_state.pet.tasks)
    conflict_warnings = scheduler.detect_conflicts(entries=requested_entries)

    st.write("Current tasks:")
    overview_col, sorted_col = st.columns(2)
    with overview_col:
        st.markdown("### All tasks")
        st.table(task_rows(st.session_state.pet.tasks))
    with sorted_col:
        st.markdown("### Sorted by time")
        st.table(task_rows(scheduler.sort_by_time()))

    open_col, completed_col = st.columns(2)
    with open_col:
        st.markdown("### Open tasks")
        open_tasks = scheduler.filter_tasks(completed=False)
        if open_tasks:
            st.table(task_rows(open_tasks))
        else:
            st.success("All current tasks are complete.")
    with completed_col:
        st.markdown("### Completed tasks")
        completed_tasks = scheduler.filter_tasks(completed=True)
        if completed_tasks:
            st.table(task_rows(completed_tasks))
        else:
            st.info("No completed tasks yet.")

    if conflict_warnings:
        for warning in conflict_warnings:
            st.warning(warning)
    else:
        st.success("No scheduling conflicts found in the requested task times.")
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Today's Schedule")

if st.button("Generate schedule"):
    sync_profiles(
        owner_name,
        int(available_minutes),
        preferences,
        pet_name,
        species,
        int(age),
        energy_level,
        health_notes,
    )
    if not st.session_state.pet.tasks:
        st.warning("Add at least one task before generating a schedule.")
    else:
        scheduler = Scheduler(
            st.session_state.owner,
            st.session_state.pet,
            st.session_state.pet.tasks,
        )
        st.session_state.daily_plan = scheduler.generate_plan()

plan = st.session_state.daily_plan
if plan is not None:
    st.success("Daily schedule generated.")
    st.table(schedule_rows(plan.selected_tasks))

    if plan.unscheduled_tasks:
        st.markdown("### Unscheduled tasks")
        st.table(task_rows(plan.unscheduled_tasks))

    explanations = plan.explain_choices()
    if explanations:
        st.markdown("### Why these tasks were chosen")
        for explanation in explanations:
            st.write(f"- {explanation}")
