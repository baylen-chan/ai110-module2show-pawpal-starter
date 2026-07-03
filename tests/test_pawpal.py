"""Quick tests for PawPal+ core behavior."""

from datetime import date, timedelta

from pawpal_system import (
    Owner,
    Pet,
    Task,
    Priority,
    Frequency,
    Scheduler,
)


def test_task_completion():
    """Calling mark_complete() changes the task's status to completed."""
    task = Task("Feeding", 10, Priority.HIGH)
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_task_addition():
    """Adding a task to a Pet increases that pet's task count."""
    pet = Pet(name="Biscuit", species="dog")
    assert len(pet.tasks) == 0
    pet.add_task(Task("Walk", 30, Priority.HIGH))
    assert len(pet.tasks) == 1


# --------------------------------------------------------------------------
# Sorting correctness
# --------------------------------------------------------------------------

def test_sort_by_time_orders_chronologically():
    """sort_by_time returns (pet, task) pairs earliest-first, regardless of
    the order they were added."""
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="cat")
    owner.add_pet(pet)

    # Added deliberately out of order: evening, morning, midday.
    pet.add_task(Task("Playtime", 20, Priority.LOW, preferred_time=1020))    # 17:00
    pet.add_task(Task("Morning walk", 30, Priority.HIGH, preferred_time=480))  # 08:00
    pet.add_task(Task("Litter change", 10, Priority.MEDIUM, preferred_time=540))  # 09:00

    scheduler = Scheduler()
    ordered = scheduler.sort_by_time(owner.get_all_tasks_with_pets())
    times = [task.preferred_time for _pet, task in ordered]

    assert times == [480, 540, 1020]
    assert times == sorted(times)


def test_sort_by_time_puts_untimed_tasks_last():
    """Tasks with no preferred_time sort to the very end."""
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="cat")
    owner.add_pet(pet)

    pet.add_task(Task("Anytime brushing", 10, Priority.LOW))  # preferred_time=None
    pet.add_task(Task("Morning walk", 30, Priority.HIGH, preferred_time=480))

    scheduler = Scheduler()
    ordered = scheduler.sort_by_time(owner.get_all_tasks_with_pets())
    descriptions = [task.description for _pet, task in ordered]

    assert descriptions == ["Morning walk", "Anytime brushing"]


# --------------------------------------------------------------------------
# Recurrence logic
# --------------------------------------------------------------------------

def test_daily_task_spawns_next_day_on_completion():
    """Marking a DAILY task complete creates a fresh task due the next day."""
    pet = Pet(name="Biscuit", species="dog")
    today = date(2026, 7, 2)
    walk = Task("Morning walk", 30, Priority.HIGH, preferred_time=480,
                frequency=Frequency.DAILY)
    pet.add_task(walk)

    assert len(pet.tasks) == 1
    next_task = pet.mark_task_complete(walk, today=today)

    # The original is now complete; a new occurrence has been added.
    assert walk.completed is True
    assert len(pet.tasks) == 2
    assert next_task is not None
    assert next_task.due_date == today + timedelta(days=1)
    assert next_task.completed is False
    # Details carry over to the next occurrence.
    assert next_task.description == "Morning walk"
    assert next_task.preferred_time == 480
    assert next_task.frequency is Frequency.DAILY


def test_weekly_task_spawns_seven_days_later():
    """A WEEKLY task's next occurrence is due seven days out."""
    pet = Pet(name="Biscuit", species="dog")
    today = date(2026, 7, 2)
    bath = Task("Bath", 30, Priority.MEDIUM, frequency=Frequency.WEEKLY)
    pet.add_task(bath)

    next_task = pet.mark_task_complete(bath, today=today)
    assert next_task.due_date == today + timedelta(weeks=1)


def test_one_off_task_does_not_recur():
    """Completing a Frequency.ONCE task creates no follow-up."""
    pet = Pet(name="Biscuit", species="dog")
    feeding = Task("Feeding", 10, Priority.HIGH)  # defaults to Frequency.ONCE
    pet.add_task(feeding)

    next_task = pet.mark_task_complete(feeding)
    assert next_task is None
    assert len(pet.tasks) == 1


# --------------------------------------------------------------------------
# Conflict detection
# --------------------------------------------------------------------------

def test_detect_conflicts_flags_duplicate_times():
    """Two tasks at the same preferred_time are flagged as a conflict."""
    owner = Owner(name="Jordan")
    biscuit = Pet(name="Biscuit", species="dog")
    owner.add_pet(biscuit)

    biscuit.add_task(Task("Morning walk", 30, Priority.HIGH, preferred_time=480))
    biscuit.add_task(Task("Vet call", 15, Priority.MEDIUM, preferred_time=480))

    conflicts = Scheduler().detect_conflicts(owner)
    assert len(conflicts) == 1
    assert "Morning walk" in conflicts[0]
    assert "Vet call" in conflicts[0]


def test_detect_conflicts_ignores_adjacent_tasks():
    """Back-to-back tasks that only touch at the boundary do not conflict."""
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="cat")
    owner.add_pet(pet)

    pet.add_task(Task("Walk", 30, Priority.HIGH, preferred_time=480))   # 08:00-08:30
    pet.add_task(Task("Feed", 10, Priority.HIGH, preferred_time=510))   # 08:30-08:40

    assert Scheduler().detect_conflicts(owner) == []


def test_detect_conflicts_ignores_completed_tasks():
    """A completed task can't clash — it won't happen again today."""
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="cat")
    owner.add_pet(pet)

    walk = Task("Walk", 30, Priority.HIGH, preferred_time=480)
    walk.mark_complete()
    pet.add_task(walk)
    pet.add_task(Task("Vet call", 15, Priority.MEDIUM, preferred_time=480))

    assert Scheduler().detect_conflicts(owner) == []
