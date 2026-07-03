"""PawPal+ system classes.

Core implementation of the four main classes: Task, Pet, Owner, Scheduler.

Design notes for clarity:
- Times are stored as minutes since midnight (an int), so 8:00 AM is 480.
  This lets the scheduler do simple math (start + duration = end) instead
  of parsing strings. Use `minutes_to_clock()` to show them as "08:00".
- Priority and Frequency are Enums so values are fixed and self-explaining
  (no "high" vs "High" typos), and priority sorts by number automatically.
- The Scheduler never reaches into a Pet's task list directly. It asks the
  Owner via `owner.get_all_tasks_with_pets()`, so each class stays in charge
  of its own data.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, IntEnum


class Priority(IntEnum):
    """How important a task is. Higher number = more important, so tasks
    sort by priority automatically."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3


class Frequency(Enum):
    """How often a task repeats."""

    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"


def minutes_to_clock(minutes: int) -> str:
    """Turn minutes-since-midnight into a readable clock string (480 -> '08:00')."""
    hours, mins = divmod(minutes, 60)
    return f"{hours:02d}:{mins:02d}"


@dataclass
class Task:
    """A single pet-care activity: a walk, feeding, meds, grooming, etc."""

    description: str
    duration_minutes: int
    priority: Priority = Priority.MEDIUM
    preferred_time: int | None = None  # minutes since midnight, e.g. 480 = 08:00
    frequency: Frequency = Frequency.ONCE
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def mark_incomplete(self) -> None:
        """Mark this task as not done."""
        self.completed = False

    def is_higher_priority_than(self, other: "Task") -> bool:
        """Return True if this task outranks ``other``."""
        return self.priority > other.priority

    def fits_in(self, remaining_minutes: int) -> bool:
        """Return True if this task fits in the remaining time budget."""
        return self.duration_minutes <= remaining_minutes


@dataclass
class ScheduledEntry:
    """One task placed on the day's timeline, with the pet it belongs to."""

    pet: "Pet"
    task: Task
    start: int  # minutes since midnight
    end: int  # minutes since midnight

    def overlaps(self, other: "ScheduledEntry") -> bool:
        """Return True if this entry's time range collides with ``other``."""
        return self.start < other.end and other.start < self.end

    def __str__(self) -> str:
        """Render this entry as a readable schedule line."""
        return (
            f"{minutes_to_clock(self.start)} — {self.task.description} "
            f"({self.task.duration_minutes} min) "
            f"[{self.pet.name}, priority: {self.task.priority.name.lower()}]"
        )


@dataclass
class Pet:
    """A pet and the care tasks that belong to it."""

    name: str
    species: str
    breed: str = ""
    age: int = 0
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a new care task to this pet."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a care task from this pet (no-op if it isn't there)."""
        if task in self.tasks:
            self.tasks.remove(task)

    def get_tasks(self) -> list[Task]:
        """Return a copy of this pet's task list."""
        return list(self.tasks)

    def pending_tasks(self) -> list[Task]:
        """Return only the tasks that aren't completed yet."""
        return [task for task in self.tasks if not task.completed]


@dataclass
class Owner:
    """A pet owner. Manages multiple pets and exposes their tasks."""

    name: str
    available_minutes: int = 240  # time budget for the day
    pets: list[Pet] = field(default_factory=list)
    preferences: dict = field(default_factory=dict)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner (no-op if it isn't there)."""
        if pet in self.pets:
            self.pets.remove(pet)

    def get_all_tasks(self) -> list[Task]:
        """Flatten every task across all of this owner's pets into one list."""
        all_tasks: list[Task] = []
        for pet in self.pets:
            all_tasks.extend(pet.get_tasks())
        return all_tasks

    def get_all_tasks_with_pets(self) -> list[tuple[Pet, Task]]:
        """Like get_all_tasks(), but keeps each task paired with its pet so
        the scheduler knows who the task is for."""
        return [(pet, task) for pet in self.pets for task in pet.get_tasks()]


@dataclass
class Scheduler:
    """The 'brain': retrieves tasks from an owner's pets, orders them by
    priority, and fits them into the available time to build a daily plan."""

    day_start: int = 480  # when the day begins, in minutes since midnight (08:00)

    def sort_by_priority(self, pairs: list[tuple[Pet, Task]]) -> list[tuple[Pet, Task]]:
        """Order (pet, task) pairs by priority (high first), then shorter
        tasks first, then by preferred time."""
        return sorted(
            pairs,
            key=lambda pair: (
                -int(pair[1].priority),
                pair[1].duration_minutes,
                pair[1].preferred_time if pair[1].preferred_time is not None else 1_440,
            ),
        )

    def build_daily_plan(
        self, owner: Owner
    ) -> tuple[list[ScheduledEntry], list[Task]]:
        """Build a plan for the owner's day.

        Returns a tuple of (scheduled_entries, skipped_tasks):
        - scheduled_entries: tasks placed back-to-back from `day_start`,
          in priority order, that fit within the owner's time budget.
        - skipped_tasks: tasks that could not fit in the remaining time.
        """
        # Ask the Owner for its pets' tasks — don't reach into Pet directly.
        pending = [
            (pet, task)
            for pet, task in owner.get_all_tasks_with_pets()
            if not task.completed
        ]
        ordered = self.sort_by_priority(pending)

        scheduled: list[ScheduledEntry] = []
        skipped: list[Task] = []
        clock = self.day_start
        remaining = owner.available_minutes

        for pet, task in ordered:
            if task.fits_in(remaining):
                entry = ScheduledEntry(
                    pet=pet,
                    task=task,
                    start=clock,
                    end=clock + task.duration_minutes,
                )
                scheduled.append(entry)
                clock = entry.end
                remaining -= task.duration_minutes
            else:
                skipped.append(task)

        return scheduled, skipped

    def format_plan(self, owner: Owner) -> str:
        """Build the plan and return it as a readable, multi-line string."""
        scheduled, skipped = self.build_daily_plan(owner)
        lines = [f"Daily plan for {owner.name}:"]
        if scheduled:
            lines.extend(f"  {entry}" for entry in scheduled)
        else:
            lines.append("  (no tasks scheduled)")
        if skipped:
            lines.append("Skipped (not enough time):")
            lines.extend(f"  - {task.description}" for task in skipped)
        return "\n".join(lines)
