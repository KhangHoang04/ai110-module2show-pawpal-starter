"""CLI demo script — verifies PawPal+ sorting, filtering, recurring tasks, and conflict detection."""

from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler


def main() -> None:
    owner = Owner(name="Jordan", available_minutes=90)

    mochi = Pet(name="Mochi", species="dog", age=3, special_needs=["joint supplement"])
    whiskers = Pet(name="Whiskers", species="cat", age=5)
    owner.add_pet(mochi)
    owner.add_pet(whiskers)

    # --- Add tasks deliberately out of order to test sorting ---
    mochi.add_task(Task(
        title="Fetch in the yard", duration_minutes=20,
        priority="low", category="enrichment", scheduled_time="10:00",
    ))
    mochi.add_task(Task(
        title="Morning walk", duration_minutes=30,
        priority="high", category="walk", scheduled_time="07:00",
        frequency="daily", due_date=date.today(),
    ))
    mochi.add_task(Task(
        title="Joint supplement", duration_minutes=5,
        priority="high", category="medicine", scheduled_time="07:45",
        frequency="daily", due_date=date.today(),
    ))

    whiskers.add_task(Task(
        title="Laser pointer play", duration_minutes=15,
        priority="low", category="enrichment", scheduled_time="10:00",
    ))
    whiskers.add_task(Task(
        title="Feed breakfast", duration_minutes=10,
        priority="high", category="feed", scheduled_time="08:00",
        frequency="daily", due_date=date.today(),
    ))
    whiskers.add_task(Task(
        title="Brush fur", duration_minutes=15,
        priority="medium", category="grooming",
    ))

    scheduler = Scheduler(owner)

    # --- 1. Sort by time ---
    print("=== Sorted by Time ===")
    for t in scheduler.sort_by_time():
        time_str = t.scheduled_time or "flex"
        print(f"  {time_str:>5}  {t.title} ({t.pet_name})")

    # --- 2. Sort by priority ---
    print("\n=== Sorted by Priority ===")
    for t in scheduler.sort_by_priority():
        print(f"  [{t.priority.upper():>6}] {t.title} ({t.pet_name})")

    # --- 3. Filter by pet ---
    print("\n=== Filter: Mochi's tasks only ===")
    for t in scheduler.filter_tasks(pet_name="Mochi"):
        print(f"  - {t.title}")

    # --- 4. Filter by completion status ---
    print("\n=== Filter: pending tasks ===")
    for t in scheduler.filter_tasks(completed=False):
        print(f"  - {t.title} ({t.pet_name})")

    # --- 5. Conflict detection ---
    print("\n=== Conflict Check ===")
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for w in conflicts:
            print(f"  WARNING: {w}")
    else:
        print("  No conflicts found.")

    # --- 6. Generate full schedule ---
    schedule = scheduler.generate_schedule()
    print("\n=== Today's Schedule ===")
    print(scheduler.explain_plan(schedule))

    # --- 7. Recurring task demo ---
    print("\n=== Recurring Task Demo ===")
    walk = next(t for t in mochi.tasks if t.title == "Morning walk")
    print(f"  Completing '{walk.title}' (due {walk.due_date}) ...")
    next_walk = scheduler.complete_task(walk)
    if next_walk:
        print(f"  Next occurrence auto-created: due {next_walk.due_date}")
    print(f"  Mochi's task count is now {len(mochi.tasks)}")


if __name__ == "__main__":
    main()
