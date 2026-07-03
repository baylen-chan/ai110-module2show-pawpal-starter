"""Quick tests for PawPal+ core behavior."""

from pawpal_system import Pet, Task, Priority


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
