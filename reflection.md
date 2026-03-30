# PawPal+ Project Reflection

## 1. System Design

**Core User Actions**

The three core actions a user should be able to perform in PawPal+:

1. **Add a Pet** — The user can register a new pet by providing its name, species, age, and any special needs (e.g., medication, dietary restrictions). This is the foundation of the system since all care tasks revolve around a specific pet.

2. **Schedule a Care Task** — The user can create care tasks for their pet such as walks, feedings, medication, grooming, or enrichment activities. Each task has a duration, priority level, and category so the scheduler can reason about how to fit it into the day.

3. **Generate and View Today's Plan** — The user can request a daily schedule that automatically prioritizes and orders their pet care tasks based on available time, task priority, and pet needs. The plan includes explanations for why tasks were ordered the way they are.

**Building Blocks**

The system is composed of four main objects:

| Class | Attributes | Methods |
|-------|-----------|---------|
| **Pet** | name, species, age, special_needs | `summary()` — returns a description of the pet |
| **Owner** | name, pets (list), available_minutes | `add_pet()`, `remove_pet()` — manage the owner's pet list |
| **Task** | title, duration_minutes, priority, category, pet_name, completed | `mark_complete()` — marks the task as done; `priority_value()` — returns numeric priority for sorting |
| **Scheduler** | owner, tasks | `generate_schedule()` — builds a prioritized daily plan within time constraints; `explain_plan()` — provides reasoning for the schedule |

**a. Initial design**

The initial UML design includes four classes: **Pet**, **Owner**, **Task**, and **Scheduler**.

- **Pet** is a dataclass that stores basic pet information (name, species, age, special needs). It has a `summary()` method to describe the pet.
- **Owner** holds the owner's name, a list of Pet objects, and their available time for the day. It can add or remove pets.
- **Task** is a dataclass representing a single care activity with a title, duration, priority (low/medium/high), category (walk/feed/medicine/grooming/enrichment), and completion status. It can convert priority to a numeric value for sorting.
- **Scheduler** is the core logic class. It takes an Owner and a list of Tasks, then generates a time-constrained daily schedule ordered by priority. It also explains why tasks were chosen and ordered the way they are.

Relationships:
- An Owner *has many* Pets (composition).
- A Task *is associated with* a Pet (by name).
- A Scheduler *uses* an Owner and a list of Tasks to produce a plan.

**b. Design changes**

After drafting the skeleton, I asked AI to review `pawpal_system.py` for missing relationships or logic bottlenecks. The review surfaced several points:

1. **Loose Pet–Task coupling**: Tasks reference a pet by `pet_name` (a string) rather than a direct `Pet` object. This means if a pet is renamed or removed, orphaned tasks could slip through undetected. For now, we keep the string reference for simplicity (it aligns with Streamlit's text-input workflow), but `Scheduler.generate_schedule()` should validate that every task's `pet_name` matches an actual pet in the owner's list.

2. **Schedule storage**: The original design required passing the schedule list into `explain_plan()` separately. The AI suggested the Scheduler could store the last generated schedule internally so the two methods stay in sync. This is a reasonable improvement we may adopt during implementation.

3. **No `can_schedule()` check**: There is no upfront validation of whether all tasks even fit within the time budget. Adding a quick feasibility check before generating the full schedule would improve user feedback.

These observations are noted for the implementation phase. The current skeleton intentionally stays minimal to avoid premature complexity.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three main constraints:

1. **Time budget** — The owner's `available_minutes` acts as a hard cap. Tasks are added to the schedule greedily until the budget is exhausted; any that don't fit are skipped.
2. **Priority** — Tasks with `scheduled_time` values are placed first (sorted by clock time), then remaining flexible tasks are filled in by priority (high > medium > low). This means a high-priority timed task at 08:00 always appears before a high-priority flexible task.
3. **Conflict avoidance** — The scheduler checks for overlapping time slots and warns the user rather than silently double-booking a pet.

Priority and time budget were chosen as the two most important constraints because a pet owner's day is fundamentally limited by how much free time they have, and some tasks (medication, feeding) are non-negotiable compared to enrichment activities.

**b. Tradeoffs**

The conflict detection algorithm checks for **overlapping time ranges** (start-to-end), not just exact start-time matches. This is more accurate but means two tasks that are back-to-back (e.g., one ending at 08:30 and another starting at 08:30) are not flagged — which is the intended behavior since they don't actually overlap.

A tradeoff is that conflict detection runs across **all pets**, not just within a single pet. Two tasks for different pets at the same time are flagged as conflicts even though, in theory, an owner could multitask (e.g., feed the cat while the dog eats). This is reasonable because the system models a single owner who must actively perform each task, so overlapping schedules represent a real constraint for most users.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
