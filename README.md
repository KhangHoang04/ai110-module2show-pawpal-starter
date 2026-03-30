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

## Smarter Scheduling

PawPal+ includes several algorithmic features beyond basic task listing:

- **Sort by time** — Tasks with a `scheduled_time` (HH:MM) are sorted chronologically; unscheduled tasks appear at the end.
- **Sort by priority** — Tasks are ranked high > medium > low for quick triage.
- **Filter tasks** — Filter by pet name, completion status, or category (walk, feed, medicine, etc.).
- **Recurring tasks** — Daily and weekly tasks automatically generate their next occurrence when marked complete, using `timedelta` for accurate date math.
- **Conflict detection** — The scheduler scans for overlapping time ranges and returns human-readable warnings instead of crashing.
- **Smart schedule generation** — Time-slotted tasks are placed first (by clock time), then flexible tasks fill remaining time by priority, all within the owner's daily time budget.

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
