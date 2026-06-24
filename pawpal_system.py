"""PawPal+ system classes (skeleton).

Class stubs derived from diagrams/uml.mmd. Attributes and method
signatures only — no scheduling logic yet.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CareTask:
    """A single unit of pet care: a walk, feeding, meds, grooming, etc."""

    name: str
    task_type: str
    duration_minutes: int
    priority: str
    preferred_time: str | None = None
    recurrence: str = "none"

    def is_higher_priority_than(self, other: "CareTask") -> bool:
        """Return True if this task outranks ``other`` for sorting."""
        raise NotImplementedError

    def fits_in(self, remaining_minutes: int) -> bool:
        """Return True if this task fits in the remaining time budget."""
        raise NotImplementedError


@dataclass
class Pet:
    """A pet and the care tasks that belong to it."""

    name: str
    species: str
    breed: str = ""
    age: int = 0
    tasks: list[CareTask] = field(default_factory=list)

    def add_task(self, task: CareTask) -> None:
        """Attach a new care task to this pet."""
        raise NotImplementedError

    def remove_task(self, task: CareTask) -> None:
        """Remove a care task from this pet."""
        raise NotImplementedError

    def edit_task(self, task: CareTask, **changes) -> None:
        """Update fields (duration, priority, etc.) on an existing task."""
        raise NotImplementedError

    def get_tasks(self) -> list[CareTask]:
        """Return all care tasks for this pet."""
        raise NotImplementedError


@dataclass
class DailyPlan:
    """The generated schedule for a single day, plus its reasoning."""

    date: str
    entries: list[tuple[str, CareTask]] = field(default_factory=list)
    skipped_tasks: list[CareTask] = field(default_factory=list)
    reasoning: str = ""

    def add_entry(self, task: CareTask, start_time: str) -> None:
        """Place a task at a start time in the plan."""
        raise NotImplementedError

    def explain(self) -> str:
        """Return a human-readable explanation of the scheduling choices."""
        raise NotImplementedError

    def to_display(self) -> str:
        """Format the plan for CLI / Streamlit output."""
        raise NotImplementedError


@dataclass
class Scheduler:
    """Builds a DailyPlan from a pet's tasks within the owner's constraints."""

    available_minutes: int
    preferences: dict = field(default_factory=dict)

    def generate_plan(self, pet: Pet) -> DailyPlan:
        """Main action: produce a DailyPlan for the given pet."""
        raise NotImplementedError

    def sort_tasks(self, tasks: list[CareTask]) -> list[CareTask]:
        """Order tasks by priority, then duration."""
        raise NotImplementedError

    def filter_to_budget(self, tasks: list[CareTask]) -> list[CareTask]:
        """Drop or defer tasks that don't fit the time budget."""
        raise NotImplementedError

    def resolve_conflicts(self, entries: list) -> list:
        """Handle overlapping time slots among scheduled entries."""
        raise NotImplementedError
