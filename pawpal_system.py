"""PawPal+ system logic — core classes for pet care scheduling."""

from dataclasses import dataclass, field
from datetime import date, timedelta


@dataclass
class Task:
    """A single pet care activity with priority, duration, and optional scheduling."""

    title: str
    duration_minutes: int
    priority: str = "medium"
    category: str = "other"
    pet_name: str = ""
    completed: bool = False
    scheduled_time: str = ""        # "HH:MM" format, e.g. "08:30"
    frequency: str = "once"         # "once", "daily", or "weekly"
    due_date: date | None = None

    def mark_complete(self) -> "Task | None":
        """Mark this task as completed. Returns a new Task for the next occurrence if recurring."""
        self.completed = True
        if self.frequency == "daily" and self.due_date:
            return Task(
                title=self.title,
                duration_minutes=self.duration_minutes,
                priority=self.priority,
                category=self.category,
                pet_name=self.pet_name,
                scheduled_time=self.scheduled_time,
                frequency=self.frequency,
                due_date=self.due_date + timedelta(days=1),
            )
        if self.frequency == "weekly" and self.due_date:
            return Task(
                title=self.title,
                duration_minutes=self.duration_minutes,
                priority=self.priority,
                category=self.category,
                pet_name=self.pet_name,
                scheduled_time=self.scheduled_time,
                frequency=self.frequency,
                due_date=self.due_date + timedelta(weeks=1),
            )
        return None

    def priority_value(self) -> int:
        """Map priority string to a numeric value (higher = more urgent)."""
        return {"high": 3, "medium": 2, "low": 1}.get(self.priority, 0)

    def end_time_minutes(self) -> int | None:
        """Return the end time in minutes from midnight, or None if unscheduled."""
        start = self._start_minutes()
        if start is None:
            return None
        return start + self.duration_minutes

    def _start_minutes(self) -> int | None:
        """Parse scheduled_time 'HH:MM' into minutes from midnight."""
        if not self.scheduled_time:
            return None
        h, m = self.scheduled_time.split(":")
        return int(h) * 60 + int(m)


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
    """The scheduling brain — sorts, filters, detects conflicts, and plans daily tasks."""

    def __init__(self, owner: Owner, tasks: list[Task] | None = None) -> None:
        self.owner = owner
        self.tasks: list[Task] = tasks if tasks is not None else owner.all_tasks()

    # ---- Sorting -----------------------------------------------------------

    def sort_by_time(self) -> list[Task]:
        """Sort tasks by scheduled_time (HH:MM). Unscheduled tasks go to the end."""
        return sorted(
            self.tasks,
            key=lambda t: (t.scheduled_time == "", t.scheduled_time),
        )

    def sort_by_priority(self) -> list[Task]:
        """Sort tasks by priority descending (high first)."""
        return sorted(self.tasks, key=lambda t: t.priority_value(), reverse=True)

    # ---- Filtering ---------------------------------------------------------

    def filter_tasks(
        self,
        pet_name: str | None = None,
        completed: bool | None = None,
        category: str | None = None,
    ) -> list[Task]:
        """Return tasks matching the given criteria."""
        result = self.tasks
        if pet_name is not None:
            result = [t for t in result if t.pet_name == pet_name]
        if completed is not None:
            result = [t for t in result if t.completed == completed]
        if category is not None:
            result = [t for t in result if t.category == category]
        return result

    # ---- Recurring tasks ---------------------------------------------------

    def complete_task(self, task: Task) -> Task | None:
        """Mark a task complete and auto-create the next occurrence if recurring."""
        next_task = task.mark_complete()
        if next_task is not None:
            self.tasks.append(next_task)
            # Also add to the pet's task list
            for pet in self.owner.pets:
                if pet.name == next_task.pet_name:
                    pet.tasks.append(next_task)
                    break
        return next_task

    # ---- Conflict detection ------------------------------------------------

    def detect_conflicts(self) -> list[str]:
        """Find tasks whose scheduled times overlap and return warning strings."""
        scheduled = [t for t in self.tasks if t.scheduled_time and not t.completed]
        scheduled.sort(key=lambda t: t.scheduled_time)
        warnings: list[str] = []
        for i in range(len(scheduled)):
            for j in range(i + 1, len(scheduled)):
                a, b = scheduled[i], scheduled[j]
                a_start = a._start_minutes()
                a_end = a.end_time_minutes()
                b_start = b._start_minutes()
                if a_start is not None and a_end is not None and b_start is not None:
                    if b_start < a_end:
                        warnings.append(
                            f"Conflict: '{a.title}' ({a.pet_name} {a.scheduled_time}–"
                            f"{a_end // 60:02d}:{a_end % 60:02d}) overlaps with "
                            f"'{b.title}' ({b.pet_name} {b.scheduled_time})"
                        )
        return warnings

    # ---- Schedule generation -----------------------------------------------

    def generate_schedule(self) -> list[Task]:
        """Build a schedule: time-slotted tasks first (by time), then remaining by priority."""
        pending = [t for t in self.tasks if not t.completed]

        timed = sorted(
            [t for t in pending if t.scheduled_time],
            key=lambda t: t.scheduled_time,
        )
        untimed = sorted(
            [t for t in pending if not t.scheduled_time],
            key=lambda t: t.priority_value(),
            reverse=True,
        )

        schedule: list[Task] = []
        remaining = self.owner.available_minutes

        for task in timed:
            if task.duration_minutes <= remaining:
                schedule.append(task)
                remaining -= task.duration_minutes

        for task in untimed:
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
        for i, task in enumerate(schedule, 1):
            time_str = task.scheduled_time if task.scheduled_time else "flex"
            freq = f" [{task.frequency}]" if task.frequency != "once" else ""
            lines.append(
                f"  {i}. [{task.priority.upper()}] {task.title} "
                f"({task.pet_name}) — {task.duration_minutes} min "
                f"@ {time_str}{freq}"
            )

        skipped = [t for t in self.tasks if not t.completed and t not in schedule]
        if skipped:
            names = ", ".join(t.title for t in skipped)
            lines.append(f"\n  Skipped (not enough time): {names}")

        lines.append(
            "\nTime-slotted tasks are placed first (by clock time), "
            "then flexible tasks fill remaining time by priority."
        )
        return "\n".join(lines)
