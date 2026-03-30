"""PawPal+ system logic — core classes for pet care scheduling."""

from dataclasses import dataclass, field


@dataclass
class Task:
    """A single pet care activity with priority and duration."""

    title: str
    duration_minutes: int
    priority: str = "medium"
    category: str = "other"
    pet_name: str = ""
    completed: bool = False

    def mark_complete(self) -> None:
        """Set this task's status to completed."""
        self.completed = True

    def priority_value(self) -> int:
        """Map priority string to a numeric value (higher = more urgent)."""
        return {"high": 3, "medium": 2, "low": 1}.get(self.priority, 0)


@dataclass
class Pet:
    """A pet with profile info and its own task list."""

    name: str
    species: str
    age: int = 0
    special_needs: list[str] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)

    def summary(self) -> str:
        """Return a one-line description of this pet."""
        needs = f" (needs: {', '.join(self.special_needs)})" if self.special_needs else ""
        return f"{self.name} the {self.species}, age {self.age}{needs}"

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        task.pet_name = self.name
        self.tasks.append(task)


@dataclass
class Owner:
    """A pet owner who manages multiple pets and a daily time budget."""

    name: str
    pets: list[Pet] = field(default_factory=list)
    available_minutes: int = 120

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> None:
        """Remove a pet by name."""
        self.pets = [p for p in self.pets if p.name != pet_name]

    def all_tasks(self) -> list[Task]:
        """Collect every task across all pets."""
        tasks: list[Task] = []
        for pet in self.pets:
            tasks.extend(pet.tasks)
        return tasks


class Scheduler:
    """The scheduling brain — retrieves, prioritises, and plans daily tasks."""

    def __init__(self, owner: Owner, tasks: list[Task] | None = None) -> None:
        self.owner = owner
        self.tasks: list[Task] = tasks if tasks is not None else owner.all_tasks()

    def generate_schedule(self) -> list[Task]:
        """Build a priority-sorted schedule that fits within available time."""
        pending = [t for t in self.tasks if not t.completed]
        pending.sort(key=lambda t: t.priority_value(), reverse=True)

        schedule: list[Task] = []
        remaining = self.owner.available_minutes
        for task in pending:
            if task.duration_minutes <= remaining:
                schedule.append(task)
                remaining -= task.duration_minutes
        return schedule

    def explain_plan(self, schedule: list[Task]) -> str:
        """Explain why the schedule is ordered and which tasks were included."""
        if not schedule:
            return "No tasks could be scheduled within the available time."

        total = sum(t.duration_minutes for t in schedule)
        lines = [
            f"Schedule for {self.owner.name} "
            f"({total}/{self.owner.available_minutes} min used):\n"
        ]
        start = 0
        for i, task in enumerate(schedule, 1):
            end = start + task.duration_minutes
            lines.append(
                f"  {i}. [{task.priority.upper()}] {task.title} "
                f"({task.pet_name}) — {task.duration_minutes} min "
                f"(min {start}–{end})"
            )
            start = end

        skipped = [t for t in self.tasks if not t.completed and t not in schedule]
        if skipped:
            names = ", ".join(t.title for t in skipped)
            lines.append(f"\n  Skipped (not enough time): {names}")

        lines.append(
            "\nTasks are ordered by priority (high > medium > low). "
            "Lower-priority tasks are dropped first when time runs out."
        )
        return "\n".join(lines)
