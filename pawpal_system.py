"""PawPal+ system logic — class skeletons derived from UML design."""

from dataclasses import dataclass, field


@dataclass
class Pet:
    """Represents a pet with basic profile information."""

    name: str
    species: str
    age: int = 0
    special_needs: list[str] = field(default_factory=list)

    def summary(self) -> str:
        """Return a short description of the pet."""
        pass


@dataclass
class Owner:
    """Represents a pet owner with their pets and daily time budget."""

    name: str
    pets: list[Pet] = field(default_factory=list)
    available_minutes: int = 120

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's list."""
        pass

    def remove_pet(self, pet_name: str) -> None:
        """Remove a pet by name."""
        pass


@dataclass
class Task:
    """Represents a single pet care task."""

    title: str
    duration_minutes: int
    priority: str = "medium"  # low, medium, high
    category: str = "other"  # walk, feed, medicine, grooming, enrichment, other
    pet_name: str = ""
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        pass

    def priority_value(self) -> int:
        """Return a numeric priority for sorting (higher = more urgent)."""
        pass


class Scheduler:
    """Builds and explains a daily care plan from tasks and constraints."""

    def __init__(self, owner: Owner, tasks: list[Task] | None = None) -> None:
        self.owner = owner
        self.tasks: list[Task] = tasks if tasks is not None else []

    def generate_schedule(self) -> list[Task]:
        """Return an ordered list of tasks that fit within the owner's available time."""
        pass

    def explain_plan(self, schedule: list[Task]) -> str:
        """Return a human-readable explanation of why the schedule is ordered this way."""
        pass
