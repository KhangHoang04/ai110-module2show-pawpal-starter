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

AI was used throughout several phases of this project:

- **Design brainstorming** — I asked the AI to identify core user actions and suggest which classes and relationships were needed. It proposed the four-class architecture (Pet, Owner, Task, Scheduler) and drafted the initial Mermaid diagram.
- **Code generation** — Agent mode generated class skeletons from the UML, then fleshed out method implementations (sorting, filtering, conflict detection, recurring tasks).
- **Code review** — After the skeleton was complete, I asked the AI to review `pawpal_system.py` for missing relationships and bottlenecks. It identified the loose string-based Pet–Task coupling and the lack of a feasibility check.
- **Test generation** — The AI drafted the test suite and suggested edge cases (zero time budget, back-to-back tasks, cross-pet conflicts).

The most helpful prompts were specific, file-scoped requests like "review `pawpal_system.py` for missing relationships" rather than broad questions. Asking for concrete edge cases was also more productive than asking generically "what should I test?"

**b. Judgment and verification**

When the AI reviewed the skeleton, it suggested changing `Task.pet_name` (a string) to a direct `Pet` object reference for stronger coupling. I chose **not** to accept this because the Streamlit UI collects pet names as text input, and converting back and forth between objects and strings would add complexity with little benefit for this project's scope. I verified my decision by confirming that the Scheduler already validates pet names against `owner.pets` during schedule generation, which catches orphaned tasks without requiring an object reference.

---

## 4. Testing and Verification

**a. What you tested**

The test suite (36 tests) covers these behaviors:

- **Task completion** — `mark_complete()` changes status; completed tasks are excluded from schedules.
- **Task addition** — Adding tasks increases a pet's count and auto-sets `pet_name`.
- **Pet & Owner basics** — `summary()` formatting, `remove_pet()`, `all_tasks()` aggregation.
- **Sorting** — `sort_by_time()` orders chronologically with unscheduled tasks last; `sort_by_priority()` ranks high > medium > low.
- **Filtering** — Filter by pet name, completion status, category, and combined criteria.
- **Recurring tasks** — Daily tasks advance by 1 day, weekly by 7 days, one-time tasks return None, attributes are preserved across recurrences.
- **Conflict detection** — Overlapping tasks flagged, non-overlapping/back-to-back/unscheduled tasks clear, cross-pet conflicts detected, completed tasks ignored.
- **Schedule generation** — Time budget respected, priority ordering, timed-before-flex, empty/zero-budget edge cases, explain_plan output.

These tests are important because the scheduler is the core "brain" of the app — if sorting, filtering, or conflict detection is broken, the daily plan will be wrong and the user will lose trust in the tool.

**b. Confidence**

Confidence: **4/5 stars**. All 36 tests pass and cover the primary happy paths and edge cases. The remaining gap is integration testing with the Streamlit UI (ensuring session state round-trips work correctly) and stress testing with a large number of tasks. If I had more time, I would add tests for:
- A pet with zero tasks going through the scheduler
- Tasks that span midnight (e.g., 23:45 + 30 min)
- Very large task lists (100+ tasks) to verify performance

---

## 5. Reflection

**a. What went well**

The CLI-first workflow was the most satisfying part. By building and verifying all logic in `main.py` and `pytest` before touching the Streamlit UI, I caught design issues early (like the need for `sort_by_time()` and conflict detection) without fighting UI state. The Scheduler's `explain_plan()` method also turned out to be a surprisingly useful debugging tool — reading the plan explanation made it easy to spot when task ordering was wrong.

**b. What you would improve**

If I had another iteration, I would redesign the conflict detection to suggest **resolutions** (e.g., "Move 'Feed' to 08:30 to avoid overlap") instead of only flagging the problem. I would also add a `ScheduleResult` dataclass that bundles the schedule, conflicts, and explanation together so the UI doesn't have to call three separate methods.

**c. Key takeaway**

The most important lesson was that **AI is most effective when you give it a narrow, well-defined scope**. Broad prompts like "build me a scheduler" produced generic code, but specific prompts like "review this file for missing relationships" or "add edge case tests for conflict detection" produced targeted, high-quality output. As the lead architect, my job was to make the design decisions and break the work into focused chunks — the AI handled the implementation within those boundaries.
