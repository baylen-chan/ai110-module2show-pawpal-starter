"""Demo script for PawPal+ — a temporary CLI testing ground.

Run with: python main.py
"""

from pawpal_system import (
    Owner,
    Pet,
    Task,
    Priority,
    Frequency,
    Scheduler,
    minutes_to_clock,
)


def show(pairs) -> None:
    """Print (pet, task) pairs one per line, with time and status."""
    if not pairs:
        print("  (none)")
        return
    for pet, task in pairs:
        when = minutes_to_clock(task.preferred_time) if task.preferred_time is not None else "  --"
        status = "done" if task.completed else "pending"
        print(f"  {when}  {task.description} [{pet.name}, {status}]")


def main() -> None:
    # Create an owner with a daily time budget.
    owner = Owner(name="Jordan", available_minutes=120)

    # Create two pets.
    biscuit = Pet(name="Biscuit", species="dog", breed="Golden Retriever", age=4)
    mochi = Pet(name="Mochi", species="cat", breed="Tabby", age=2)
    owner.add_pet(biscuit)
    owner.add_pet(mochi)

    # Add tasks deliberately OUT OF ORDER (evening, then morning, then midday)
    # so the sort has something real to do.
    mochi.add_task(
        Task("Playtime", 20, Priority.LOW, preferred_time=1020, frequency=Frequency.DAILY)  # 17:00
    )
    biscuit.add_task(
        Task("Feeding", 10, Priority.HIGH, preferred_time=510, frequency=Frequency.DAILY)  # 08:30
    )
    mochi.add_task(
        Task("Litter change", 10, Priority.MEDIUM, preferred_time=540)  # 09:00
    )
    biscuit.add_task(
        Task("Morning walk", 30, Priority.HIGH, preferred_time=480, frequency=Frequency.DAILY)  # 08:00
    )

    # Mark one task done so the status filter has something to hide.
    feeding = next(task for task in biscuit.tasks if task.description == "Feeding")
    feeding.mark_complete()

    scheduler = Scheduler()

    print("Tasks in the order they were added")
    print("=" * 40)
    show(owner.get_all_tasks_with_pets())

    print("\nSorted by time (earliest first)")
    print("=" * 40)
    show(scheduler.sort_by_time(owner.get_all_tasks_with_pets()))

    print("\nFilter: only pending tasks")
    print("=" * 40)
    show(owner.filter_tasks(completed=False))

    print("\nFilter: only Mochi's tasks")
    print("=" * 40)
    show(owner.filter_tasks(pet_name="Mochi"))

    print("\nCombined: Mochi's pending tasks, sorted by time")
    print("=" * 40)
    show(scheduler.sort_by_time(owner.filter_tasks(pet_name="Mochi", completed=False)))

    print("\nConflict detection: two tasks scheduled at the same time")
    print("=" * 40)
    # Biscuit has both a walk (08:00) and now a vet call at the SAME time.
    biscuit.add_task(
        Task("Vet call", 15, Priority.MEDIUM, preferred_time=480)  # 08:00 — clashes with Morning walk
    )
    conflicts = scheduler.detect_conflicts(owner)
    if conflicts:
        for warning in conflicts:
            print(f"  ! {warning}")
    else:
        print("  No conflicts found.")

    print("\nRecurring tasks: completing a daily task spawns the next one")
    print("=" * 40)
    walk = next(task for task in biscuit.tasks if task.description == "Morning walk")
    print(f"  Before: Biscuit has {len(biscuit.tasks)} task(s); "
          f"'{walk.description}' is {walk.frequency.value}, completed={walk.completed}")
    next_walk = biscuit.mark_task_complete(walk)
    print(f"  After:  Biscuit has {len(biscuit.tasks)} task(s)")
    print(f"  New occurrence auto-created -> due {next_walk.due_date} "
          f"(completed={next_walk.completed})")

    # Build and print today's schedule.
    print("\nToday's Schedule")
    print("=" * 40)
    print(scheduler.format_plan(owner))


if __name__ == "__main__":
    main()
