# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Sample of the CLI output from running `python main.py`:

```
Tasks in the order they were added
========================================
  08:30  Feeding [Biscuit, done]
  08:00  Morning walk [Biscuit, pending]
  17:00  Playtime [Mochi, pending]
  09:00  Litter change [Mochi, pending]

Sorted by time (earliest first)
========================================
  08:00  Morning walk [Biscuit, pending]
  08:30  Feeding [Biscuit, done]
  09:00  Litter change [Mochi, pending]
  17:00  Playtime [Mochi, pending]

Filter: only pending tasks
========================================
  08:00  Morning walk [Biscuit, pending]
  17:00  Playtime [Mochi, pending]
  09:00  Litter change [Mochi, pending]

Filter: only Mochi's tasks
========================================
  17:00  Playtime [Mochi, pending]
  09:00  Litter change [Mochi, pending]

Combined: Mochi's pending tasks, sorted by time
========================================
  09:00  Litter change [Mochi, pending]
  17:00  Playtime [Mochi, pending]

Conflict detection: two tasks scheduled at the same time
========================================
  ! Conflict: 'Morning walk' (Biscuit, 08:00-08:30) overlaps 'Vet call' (Biscuit, 08:00-08:15)

Recurring tasks: completing a daily task spawns the next one
========================================
  Before: Biscuit has 3 task(s); 'Morning walk' is daily, completed=False
  After:  Biscuit has 4 task(s)
  New occurrence auto-created -> due 2026-07-03 (completed=False)

Today's Schedule
========================================
Daily plan for Jordan:
  08:00 — Morning walk (30 min) [Biscuit, priority: high]
  08:30 — Litter change (10 min) [Mochi, priority: medium]
  08:40 — Vet call (15 min) [Biscuit, priority: medium]
  08:55 — Playtime (20 min) [Mochi, priority: low]
Warnings:
  ! Conflict: 'Vet call' (Biscuit, 08:00-08:15) overlaps 'Morning walk' (Biscuit, 08:00-08:30)
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

PawPal+ adds four small algorithms on top of the core classes to make the daily plan more useful.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()`, `Scheduler.sort_by_priority()` | `sort_by_time()` orders `(pet, task)` pairs chronologically by `preferred_time` (tasks with no set time sort last); `sort_by_priority()` orders by priority, then shorter tasks, then time. Both use `sorted()` with a `lambda` key. |
| Filtering | `Owner.filter_tasks(pet_name=..., completed=...)` | Returns `(pet, task)` pairs, optionally narrowed by pet name and/or completion status. Each filter is independent, so you can combine them (e.g. "Mochi's pending tasks") or use neither. |
| Conflict detection | `Scheduler.detect_conflicts()`, `ScheduledEntry.overlaps()` | Builds a time interval for each timed task and compares every pair with `overlaps()`. Returns a list of warning strings (empty if none) — it warns rather than crashing or auto-rescheduling. |
| Recurring tasks | `Pet.mark_task_complete()`, `Task.next_occurrence()` | Completing a `DAILY`/`WEEKLY` task auto-creates its next occurrence on the pet. `next_occurrence()` uses `datetime.timedelta` to set the new `due_date` (daily → +1 day, weekly → +7 days); `ONCE` tasks return `None`. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
