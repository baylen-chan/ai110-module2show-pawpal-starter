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

from dataclasses import dataclass, field, replace
from datetime import date, timedelta
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
    due_date: date | None = None  # which calendar day this task is due

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def is_recurring(self) -> bool:
        """Return True if this task repeats (daily or weekly, not one-off)."""
        return self.frequency in (Frequency.DAILY, Frequency.WEEKLY)

    def next_occurrence(self, from_date: date | None = None) -> "Task | None":
        """Return a fresh, uncompleted copy of this task for its next due date,
        or None if it doesn't repeat (Frequency.ONCE).

        The gap is computed with datetime.timedelta so date math is exact and
        handles month/year rollovers for us: DAILY adds one day, WEEKLY adds
        seven. We advance from this task's own due_date when it has one,
        otherwise from `from_date` (defaults to today) — so a completed daily
        task becomes due "today + 1 day".
        """
        if self.frequency is Frequency.DAILY:
            gap = timedelta(days=1)
        elif self.frequency is Frequency.WEEKLY:
            gap = timedelta(weeks=1)
        else:
            return None

        base = self.due_date or from_date or date.today()
        # replace() copies every field, then overrides just these two.
        return replace(self, due_date=base + gap, completed=False)

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

    def mark_task_complete(self, task: Task, today: date | None = None) -> Task | None:
        """Mark ``task`` complete and, if it recurs, auto-schedule its next
        occurrence on this pet.

        This is the single place where completion and frequency meet: a plain
        ``task.mark_complete()`` only flips the flag, but going through the pet
        lets a daily/weekly task spawn its follow-up so care keeps repeating.
        Returns the newly-created next task (or None for a one-off task).
        """
        task.mark_complete()
        next_task = task.next_occurrence(from_date=today)
        if next_task is not None:
            self.add_task(next_task)
        return next_task


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

    def filter_tasks(
        self, pet_name: str | None = None, completed: bool | None = None
    ) -> list[tuple[Pet, Task]]:
        """Return (pet, task) pairs, optionally filtered by pet name and/or
        completion status.

        Each filter is independent and only applies when you pass it:
        - pet_name=None  -> tasks for every pet; "Mochi" -> just Mochi's.
        - completed=None -> any status; True -> only done; False -> only pending.
        """
        pairs = self.get_all_tasks_with_pets()
        if pet_name is not None:
            pairs = [(pet, task) for pet, task in pairs if pet.name == pet_name]
        if completed is not None:
            pairs = [(pet, task) for pet, task in pairs if task.completed == completed]
        return pairs


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

    def sort_by_time(self, pairs: list[tuple[Pet, Task]]) -> list[tuple[Pet, Task]]:
        """Order (pet, task) pairs chronologically by preferred_time (earliest
        first). Tasks with no preferred_time sort to the very end.

        The lambda is the sort "key": sorted() calls it on each pair and orders
        by whatever it returns. Because preferred_time is stored as minutes since
        midnight (an int), a plain numeric compare already gives clock order.

        Tip: if you ever store times as zero-padded "HH:MM" strings instead,
        the same trick works with `key=lambda pair: pair[1].preferred_time`
        because "08:00" < "09:30" < "17:00" sorts correctly as text. The `or`
        fallback below would become `... or "99:99"` to push None-times last.
        """
        return sorted(
            pairs,
            key=lambda pair: (
                pair[1].preferred_time if pair[1].preferred_time is not None else 1_440
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

    def detect_conflicts(self, owner: Owner) -> list[str]:
        """Return a warning string for every pair of tasks whose *preferred*
        time slots overlap. Returns an empty list when the day is clash-free.

        This is deliberately lightweight and non-fatal: a conflict produces a
        message, never an exception, so the rest of the plan still prints. Only
        tasks with a preferred_time can clash — a task with no set time is
        flexible and just gets slotted wherever there's room.
        """
        # Turn each timed, pending task into an interval on the day's clock.
        entries = [
            ScheduledEntry(
                pet=pet,
                task=task,
                start=task.preferred_time,
                end=task.preferred_time + task.duration_minutes,
            )
            for pet, task in owner.get_all_tasks_with_pets()
            if task.preferred_time is not None and not task.completed
        ]

        # Compare every pair once (n is small for a pet-care day). Reuse the
        # overlaps() check ScheduledEntry already provides.
        warnings: list[str] = []
        for i in range(len(entries)):
            for j in range(i + 1, len(entries)):
                a, b = entries[i], entries[j]
                if a.overlaps(b):
                    warnings.append(
                        f"Conflict: '{a.task.description}' ({a.pet.name}, "
                        f"{minutes_to_clock(a.start)}-{minutes_to_clock(a.end)}) "
                        f"overlaps '{b.task.description}' ({b.pet.name}, "
                        f"{minutes_to_clock(b.start)}-{minutes_to_clock(b.end)})"
                    )
        return warnings

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
        conflicts = self.detect_conflicts(owner)
        if conflicts:
            lines.append("Warnings:")
            lines.extend(f"  ! {warning}" for warning in conflicts)
        return "\n".join(lines)
