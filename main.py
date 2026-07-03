"""Demo script for PawPal+ — a temporary CLI testing ground.

Run with: python main.py
"""

from pawpal_system import Owner, Pet, Task, Priority, Frequency, Scheduler


def main() -> None:
    # Create an owner with a daily time budget.
    owner = Owner(name="Jordan", available_minutes=120)

    # Create two pets.
    biscuit = Pet(name="Biscuit", species="dog", breed="Golden Retriever", age=4)
    mochi = Pet(name="Mochi", species="cat", breed="Tabby", age=2)
    owner.add_pet(biscuit)
    owner.add_pet(mochi)

    # Add tasks with different preferred times (minutes since midnight).
    biscuit.add_task(
        Task("Morning walk", 30, Priority.HIGH, preferred_time=480, frequency=Frequency.DAILY)
    )
    biscuit.add_task(
        Task("Feeding", 10, Priority.HIGH, preferred_time=510, frequency=Frequency.DAILY)
    )
    mochi.add_task(
        Task("Litter change", 10, Priority.MEDIUM, preferred_time=540)
    )
    mochi.add_task(
        Task("Playtime", 20, Priority.LOW, preferred_time=1020, frequency=Frequency.DAILY)
    )

    # Build and print today's schedule.
    scheduler = Scheduler()
    print("Today's Schedule")
    print("=" * 40)
    print(scheduler.format_plan(owner))


if __name__ == "__main__":
    main()
