"""Tests for PawPal+ core logic."""

from pawpal_system import Owner, Pet, Task, Scheduler


class TestTaskCompletion:
    def test_mark_complete_changes_status(self):
        task = Task(title="Walk", duration_minutes=30)
        assert task.completed is False
        task.mark_complete()
        assert task.completed is True

    def test_completed_task_excluded_from_schedule(self):
        owner = Owner(name="Jo", available_minutes=60)
        pet = Pet(name="Rex", species="dog")
        owner.add_pet(pet)
        task = Task(title="Walk", duration_minutes=20, priority="high")
        pet.add_task(task)
        task.mark_complete()

        schedule = Scheduler(owner).generate_schedule()
        assert task not in schedule


class TestTaskAddition:
    def test_add_task_increases_pet_task_count(self):
        pet = Pet(name="Mochi", species="dog")
        assert len(pet.tasks) == 0
        pet.add_task(Task(title="Feed", duration_minutes=10))
        assert len(pet.tasks) == 1
        pet.add_task(Task(title="Walk", duration_minutes=30))
        assert len(pet.tasks) == 2

    def test_add_task_sets_pet_name(self):
        pet = Pet(name="Mochi", species="dog")
        task = Task(title="Feed", duration_minutes=10)
        pet.add_task(task)
        assert task.pet_name == "Mochi"


class TestScheduler:
    def test_schedule_respects_time_budget(self):
        owner = Owner(name="Jo", available_minutes=30)
        pet = Pet(name="Rex", species="dog")
        owner.add_pet(pet)
        pet.add_task(Task(title="Walk", duration_minutes=20, priority="high"))
        pet.add_task(Task(title="Play", duration_minutes=20, priority="low"))

        schedule = Scheduler(owner).generate_schedule()
        total = sum(t.duration_minutes for t in schedule)
        assert total <= owner.available_minutes

    def test_schedule_prioritises_high_tasks(self):
        owner = Owner(name="Jo", available_minutes=25)
        pet = Pet(name="Rex", species="dog")
        owner.add_pet(pet)
        pet.add_task(Task(title="Low task", duration_minutes=20, priority="low"))
        pet.add_task(Task(title="High task", duration_minutes=20, priority="high"))

        schedule = Scheduler(owner).generate_schedule()
        assert len(schedule) == 1
        assert schedule[0].title == "High task"
