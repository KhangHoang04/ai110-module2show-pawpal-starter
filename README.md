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

## Demo

<!-- TODO: Replace with your actual screenshot after running `streamlit run app.py` -->
<a href="demo_screenshot.png" target="_blank"><img src='demo_screenshot.png' title='PawPal App' width='' alt='PawPal App' /></a>

### System Architecture

<a href="uml_final.png" target="_blank"><img src='uml_final.png' title='PawPal+ UML Diagram' width='' alt='PawPal+ Class Diagram' /></a>

## Features

- **Owner & Pet management** — Register multiple pets with name, species, age, and special needs
- **Task creation** — Add care tasks with duration, priority, category, scheduled time, and recurrence
- **Smart scheduling** — Generates a daily plan: timed tasks first (by clock), then flexible tasks by priority, within the owner's time budget
- **Sorting** — Sort tasks chronologically or by priority
- **Filtering** — Filter by pet, completion status, or category
- **Recurring tasks** — Daily/weekly tasks auto-generate the next occurrence when completed
- **Conflict detection** — Warns when task time ranges overlap (including across pets)
- **Plan explanation** — The scheduler explains why tasks are ordered the way they are and which were skipped

## Smarter Scheduling

PawPal+ includes several algorithmic features beyond basic task listing:

- **Sort by time** — Tasks with a `scheduled_time` (HH:MM) are sorted chronologically; unscheduled tasks appear at the end.
- **Sort by priority** — Tasks are ranked high > medium > low for quick triage.
- **Filter tasks** — Filter by pet name, completion status, or category (walk, feed, medicine, etc.).
- **Recurring tasks** — Daily and weekly tasks automatically generate their next occurrence when marked complete, using `timedelta` for accurate date math.
- **Conflict detection** — The scheduler scans for overlapping time ranges and returns human-readable warnings instead of crashing.
- **Smart schedule generation** — Time-slotted tasks are placed first (by clock time), then flexible tasks fill remaining time by priority, all within the owner's daily time budget.

## Testing PawPal+

Run the full test suite with:

```bash
python -m pytest tests/ -v
```

The suite includes **36 tests** covering:

| Area | What's tested |
|------|---------------|
| Task basics | Completion, priority mapping |
| Pet & Owner | Summaries, add/remove pets, task aggregation |
| Sorting | Chronological order, priority order, unscheduled-last |
| Filtering | By pet, status, category, combined criteria |
| Recurring tasks | Daily/weekly recurrence, attribute preservation, one-time tasks |
| Conflict detection | Overlapping ranges, back-to-back, cross-pet, completed-task exclusion |
| Schedule generation | Time budget, priority ordering, timed-before-flex, edge cases |

**Confidence level: 4/5** — All tests pass; remaining gap is Streamlit integration and midnight-spanning tasks.

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
