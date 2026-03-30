"""CLI demo script — verifies PawPal+ logic in the terminal."""

from pawpal_system import Owner, Pet, Task, Scheduler


def main() -> None:
    # --- Create owner ---
    owner = Owner(name="Jordan", available_minutes=90)

    # --- Create pets ---
    mochi = Pet(name="Mochi", species="dog", age=3, special_needs=["joint supplement"])
    whiskers = Pet(name="Whiskers", species="cat", age=5)

    owner.add_pet(mochi)
    owner.add_pet(whiskers)

    # --- Add tasks to pets ---
    mochi.add_task(Task(title="Morning walk", duration_minutes=30, priority="high", category="walk"))
    mochi.add_task(Task(title="Joint supplement", duration_minutes=5, priority="high", category="medicine"))
    mochi.add_task(Task(title="Fetch in the yard", duration_minutes=20, priority="low", category="enrichment"))

    whiskers.add_task(Task(title="Feed breakfast", duration_minutes=10, priority="high", category="feed"))
    whiskers.add_task(Task(title="Brush fur", duration_minutes=15, priority="medium", category="grooming"))
    whiskers.add_task(Task(title="Laser pointer play", duration_minutes=15, priority="low", category="enrichment"))

    # --- Print pet summaries ---
    print("=== Pets ===")
    for pet in owner.pets:
        print(f"  - {pet.summary()}")

    # --- Generate and display schedule ---
    scheduler = Scheduler(owner)
    schedule = scheduler.generate_schedule()

    print()
    print("=== Today's Schedule ===")
    print(scheduler.explain_plan(schedule))


if __name__ == "__main__":
    main()
