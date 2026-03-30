"""Tests for PawPal+ core logic — happy paths and edge cases."""

from datetime import date, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler


# --- Task basics -----------------------------------------------------------

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

    def test_priority_value_mapping(self):
        assert Task(title="t", duration_minutes=1, priority="high").priority_value() == 3
        assert Task(title="t", duration_minutes=1, priority="medium").priority_value() == 2
        assert Task(title="t", duration_minutes=1, priority="low").priority_value() == 1
        assert Task(title="t", duration_minutes=1, priority="unknown").priority_value() == 0


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


# --- Pet & Owner -----------------------------------------------------------

class TestPetOwner:
    def test_pet_summary_with_special_needs(self):
        pet = Pet(name="Mochi", species="dog", age=3, special_needs=["joint supplement"])
        assert "Mochi" in pet.summary()
        assert "joint supplement" in pet.summary()

    def test_pet_summary_without_special_needs(self):
        pet = Pet(name="Luna", species="cat", age=2)
        assert "needs" not in pet.summary()

    def test_owner_remove_pet(self):
        owner = Owner(name="Jo")
        owner.add_pet(Pet(name="Rex", species="dog"))
        owner.add_pet(Pet(name="Luna", species="cat"))
        owner.remove_pet("Rex")
        assert len(owner.pets) == 1
        assert owner.pets[0].name == "Luna"

    def test_owner_all_tasks_aggregates_across_pets(self):
        owner = Owner(name="Jo")
        dog = Pet(name="Rex", species="dog")
        cat = Pet(name="Luna", species="cat")
        owner.add_pet(dog)
        owner.add_pet(cat)
        dog.add_task(Task(title="Walk", duration_minutes=30))
        cat.add_task(Task(title="Feed", duration_minutes=10))
        assert len(owner.all_tasks()) == 2


# --- Sorting ---------------------------------------------------------------

class TestSorting:
    def test_sort_by_time_orders_by_scheduled_time(self):
        owner = Owner(name="Jo")
        pet = Pet(name="Rex", species="dog")
        owner.add_pet(pet)
        pet.add_task(Task(title="Late", duration_minutes=10, scheduled_time="10:00"))
        pet.add_task(Task(title="Early", duration_minutes=10, scheduled_time="07:00"))
        pet.add_task(Task(title="Mid", duration_minutes=10, scheduled_time="09:00"))

        result = Scheduler(owner).sort_by_time()
        assert [t.title for t in result] == ["Early", "Mid", "Late"]

    def test_sort_by_time_puts_unscheduled_last(self):
        owner = Owner(name="Jo")
        pet = Pet(name="Rex", species="dog")
        owner.add_pet(pet)
        pet.add_task(Task(title="Flex", duration_minutes=10))
        pet.add_task(Task(title="Timed", duration_minutes=10, scheduled_time="08:00"))

        result = Scheduler(owner).sort_by_time()
        assert result[0].title == "Timed"
        assert result[1].title == "Flex"

    def test_sort_by_priority(self):
        owner = Owner(name="Jo")
        pet = Pet(name="Rex", species="dog")
        owner.add_pet(pet)
        pet.add_task(Task(title="Low", duration_minutes=10, priority="low"))
        pet.add_task(Task(title="High", duration_minutes=10, priority="high"))
        pet.add_task(Task(title="Med", duration_minutes=10, priority="medium"))

        result = Scheduler(owner).sort_by_priority()
        assert [t.title for t in result] == ["High", "Med", "Low"]


# --- Filtering -------------------------------------------------------------

class TestFiltering:
    def test_filter_by_pet_name(self):
        owner = Owner(name="Jo")
        dog = Pet(name="Rex", species="dog")
        cat = Pet(name="Luna", species="cat")
        owner.add_pet(dog)
        owner.add_pet(cat)
        dog.add_task(Task(title="Walk", duration_minutes=30))
        cat.add_task(Task(title="Feed", duration_minutes=10))

        result = Scheduler(owner).filter_tasks(pet_name="Rex")
        assert len(result) == 1
        assert result[0].title == "Walk"

    def test_filter_by_completed(self):
        owner = Owner(name="Jo")
        pet = Pet(name="Rex", species="dog")
        owner.add_pet(pet)
        t1 = Task(title="Done", duration_minutes=10)
        t1.mark_complete()
        t2 = Task(title="Pending", duration_minutes=10)
        pet.add_task(t1)
        pet.add_task(t2)

        result = Scheduler(owner).filter_tasks(completed=False)
        assert len(result) == 1
        assert result[0].title == "Pending"

    def test_filter_by_category(self):
        owner = Owner(name="Jo")
        pet = Pet(name="Rex", species="dog")
        owner.add_pet(pet)
        pet.add_task(Task(title="Walk", duration_minutes=30, category="walk"))
        pet.add_task(Task(title="Feed", duration_minutes=10, category="feed"))

        result = Scheduler(owner).filter_tasks(category="walk")
        assert len(result) == 1
        assert result[0].title == "Walk"

    def test_filter_combined_criteria(self):
        owner = Owner(name="Jo")
        pet = Pet(name="Rex", species="dog")
        owner.add_pet(pet)
        pet.add_task(Task(title="Walk", duration_minutes=30, category="walk"))
        pet.add_task(Task(title="Feed", duration_minutes=10, category="feed"))

        result = Scheduler(owner).filter_tasks(pet_name="Rex", category="feed")
        assert len(result) == 1
        assert result[0].title == "Feed"


# --- Recurring tasks -------------------------------------------------------

class TestRecurring:
    def test_daily_task_creates_next_occurrence(self):
        today = date.today()
        task = Task(
            title="Walk", duration_minutes=30,
            frequency="daily", due_date=today,
        )
        next_task = task.mark_complete()
        assert task.completed is True
        assert next_task is not None
        assert next_task.due_date == today + timedelta(days=1)
        assert next_task.completed is False

    def test_weekly_task_creates_next_occurrence(self):
        today = date.today()
        task = Task(
            title="Grooming", duration_minutes=60,
            frequency="weekly", due_date=today,
        )
        next_task = task.mark_complete()
        assert next_task is not None
        assert next_task.due_date == today + timedelta(weeks=1)

    def test_one_time_task_returns_none(self):
        task = Task(title="Vet visit", duration_minutes=120, frequency="once")
        next_task = task.mark_complete()
        assert next_task is None

    def test_recurring_without_due_date_returns_none(self):
        task = Task(title="Walk", duration_minutes=30, frequency="daily")
        next_task = task.mark_complete()
        assert next_task is None

    def test_scheduler_complete_task_adds_next_to_list(self):
        owner = Owner(name="Jo")
        pet = Pet(name="Rex", species="dog")
        owner.add_pet(pet)
        task = Task(
            title="Walk", duration_minutes=30,
            frequency="daily", due_date=date.today(),
        )
        pet.add_task(task)

        scheduler = Scheduler(owner)
        scheduler.complete_task(task)
        assert len(scheduler.tasks) == 2
        assert len(pet.tasks) == 2

    def test_next_occurrence_preserves_attributes(self):
        task = Task(
            title="Walk", duration_minutes=30, priority="high",
            category="walk", pet_name="Rex", scheduled_time="07:00",
            frequency="daily", due_date=date.today(),
        )
        next_task = task.mark_complete()
        assert next_task is not None
        assert next_task.title == "Walk"
        assert next_task.priority == "high"
        assert next_task.category == "walk"
        assert next_task.pet_name == "Rex"
        assert next_task.scheduled_time == "07:00"


# --- Conflict detection ----------------------------------------------------

class TestConflictDetection:
    def test_overlapping_tasks_detected(self):
        owner = Owner(name="Jo")
        pet = Pet(name="Rex", species="dog")
        owner.add_pet(pet)
        pet.add_task(Task(title="Walk", duration_minutes=30, scheduled_time="08:00"))
        pet.add_task(Task(title="Feed", duration_minutes=15, scheduled_time="08:15"))

        warnings = Scheduler(owner).detect_conflicts()
        assert len(warnings) == 1
        assert "Walk" in warnings[0]
        assert "Feed" in warnings[0]

    def test_no_conflict_when_tasks_dont_overlap(self):
        owner = Owner(name="Jo")
        pet = Pet(name="Rex", species="dog")
        owner.add_pet(pet)
        pet.add_task(Task(title="Walk", duration_minutes=30, scheduled_time="08:00"))
        pet.add_task(Task(title="Feed", duration_minutes=15, scheduled_time="09:00"))

        warnings = Scheduler(owner).detect_conflicts()
        assert len(warnings) == 0

    def test_no_conflict_for_unscheduled_tasks(self):
        owner = Owner(name="Jo")
        pet = Pet(name="Rex", species="dog")
        owner.add_pet(pet)
        pet.add_task(Task(title="Walk", duration_minutes=30))
        pet.add_task(Task(title="Feed", duration_minutes=15))

        warnings = Scheduler(owner).detect_conflicts()
        assert len(warnings) == 0

    def test_back_to_back_tasks_no_conflict(self):
        owner = Owner(name="Jo")
        pet = Pet(name="Rex", species="dog")
        owner.add_pet(pet)
        pet.add_task(Task(title="Walk", duration_minutes=30, scheduled_time="08:00"))
        pet.add_task(Task(title="Feed", duration_minutes=15, scheduled_time="08:30"))

        warnings = Scheduler(owner).detect_conflicts()
        assert len(warnings) == 0

    def test_exact_same_time_is_conflict(self):
        owner = Owner(name="Jo")
        pet = Pet(name="Rex", species="dog")
        owner.add_pet(pet)
        pet.add_task(Task(title="Walk", duration_minutes=30, scheduled_time="08:00"))
        pet.add_task(Task(title="Feed", duration_minutes=15, scheduled_time="08:00"))

        warnings = Scheduler(owner).detect_conflicts()
        assert len(warnings) == 1

    def test_cross_pet_conflict_detected(self):
        owner = Owner(name="Jo")
        dog = Pet(name="Rex", species="dog")
        cat = Pet(name="Luna", species="cat")
        owner.add_pet(dog)
        owner.add_pet(cat)
        dog.add_task(Task(title="Walk Rex", duration_minutes=30, scheduled_time="08:00"))
        cat.add_task(Task(title="Feed Luna", duration_minutes=15, scheduled_time="08:10"))

        warnings = Scheduler(owner).detect_conflicts()
        assert len(warnings) == 1

    def test_completed_tasks_ignored_in_conflict_check(self):
        owner = Owner(name="Jo")
        pet = Pet(name="Rex", species="dog")
        owner.add_pet(pet)
        t1 = Task(title="Walk", duration_minutes=30, scheduled_time="08:00")
        t2 = Task(title="Feed", duration_minutes=15, scheduled_time="08:10")
        t1.completed = True
        pet.add_task(t1)
        pet.add_task(t2)

        warnings = Scheduler(owner).detect_conflicts()
        assert len(warnings) == 0


# --- Schedule generation ---------------------------------------------------

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

    def test_timed_tasks_come_before_flex(self):
        owner = Owner(name="Jo", available_minutes=120)
        pet = Pet(name="Rex", species="dog")
        owner.add_pet(pet)
        pet.add_task(Task(title="Flex", duration_minutes=10, priority="high"))
        pet.add_task(Task(title="Timed", duration_minutes=10, scheduled_time="08:00"))

        schedule = Scheduler(owner).generate_schedule()
        assert schedule[0].title == "Timed"

    def test_empty_schedule_when_no_tasks(self):
        owner = Owner(name="Jo", available_minutes=60)
        pet = Pet(name="Rex", species="dog")
        owner.add_pet(pet)

        scheduler = Scheduler(owner)
        schedule = scheduler.generate_schedule()
        assert schedule == []
        assert "No tasks" in scheduler.explain_plan(schedule)

    def test_zero_time_budget_schedules_nothing(self):
        owner = Owner(name="Jo", available_minutes=0)
        pet = Pet(name="Rex", species="dog")
        owner.add_pet(pet)
        pet.add_task(Task(title="Walk", duration_minutes=10))

        schedule = Scheduler(owner).generate_schedule()
        assert schedule == []

    def test_task_exactly_fills_budget(self):
        owner = Owner(name="Jo", available_minutes=30)
        pet = Pet(name="Rex", species="dog")
        owner.add_pet(pet)
        pet.add_task(Task(title="Walk", duration_minutes=30))

        schedule = Scheduler(owner).generate_schedule()
        assert len(schedule) == 1

    def test_explain_plan_lists_skipped_tasks(self):
        owner = Owner(name="Jo", available_minutes=20)
        pet = Pet(name="Rex", species="dog")
        owner.add_pet(pet)
        pet.add_task(Task(title="Walk", duration_minutes=30, priority="high"))
        pet.add_task(Task(title="Feed", duration_minutes=10, priority="medium"))

        scheduler = Scheduler(owner)
        schedule = scheduler.generate_schedule()
        explanation = scheduler.explain_plan(schedule)
        assert "Skipped" in explanation
        assert "Walk" in explanation
