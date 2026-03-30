"""PawPal+ Streamlit UI — connected to the scheduling backend."""

import streamlit as st
from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.caption("A smart pet care planning assistant")

# ---- Session state init ----------------------------------------------------

if "owner" not in st.session_state:
    st.session_state.owner = None
if "pets" not in st.session_state:
    st.session_state.pets = []
if "setup_done" not in st.session_state:
    st.session_state.setup_done = False

# ---- Step 1: Owner + Pet setup --------------------------------------------

st.subheader("1. Owner & Pet Info")

col_owner, col_time = st.columns(2)
with col_owner:
    owner_name = st.text_input("Owner name", value="Jordan")
with col_time:
    available_minutes = st.number_input(
        "Available time today (min)", min_value=10, max_value=480, value=120
    )

st.markdown("**Add a pet**")
col_pn, col_sp, col_age = st.columns(3)
with col_pn:
    pet_name_input = st.text_input("Pet name", value="Mochi")
with col_sp:
    species_input = st.selectbox("Species", ["dog", "cat", "rabbit", "bird", "other"])
with col_age:
    age_input = st.number_input("Age", min_value=0, max_value=30, value=3)
special_needs_input = st.text_input(
    "Special needs (comma-separated, optional)", value=""
)

if st.button("Add pet"):
    needs = [s.strip() for s in special_needs_input.split(",") if s.strip()]
    new_pet = Pet(
        name=pet_name_input,
        species=species_input,
        age=age_input,
        special_needs=needs,
    )
    st.session_state.pets.append(new_pet)
    st.success(f"Added {new_pet.summary()}")

if st.session_state.pets:
    st.markdown("**Your pets:**")
    for p in st.session_state.pets:
        st.write(f"- {p.summary()}")

st.divider()

# ---- Step 2: Tasks --------------------------------------------------------

st.subheader("2. Care Tasks")
st.caption("Add tasks for your pets. The scheduler will sort and plan them for you.")

# Pick which pet this task belongs to
pet_names = [p.name for p in st.session_state.pets]
if not pet_names:
    st.info("Add at least one pet above before adding tasks.")
    st.stop()

col1, col2 = st.columns(2)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    task_pet = st.selectbox("For which pet?", pet_names)

col3, col4, col5 = st.columns(3)
with col3:
    duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
with col4:
    priority = st.selectbox("Priority", ["high", "medium", "low"])
with col5:
    category = st.selectbox(
        "Category", ["walk", "feed", "medicine", "grooming", "enrichment", "other"]
    )

col6, col7 = st.columns(2)
with col6:
    scheduled_time = st.text_input("Scheduled time (HH:MM, optional)", value="")
with col7:
    frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])

if st.button("Add task"):
    pet_obj = next(p for p in st.session_state.pets if p.name == task_pet)
    due = date.today() if frequency != "once" else None
    new_task = Task(
        title=task_title,
        duration_minutes=int(duration),
        priority=priority,
        category=category,
        scheduled_time=scheduled_time,
        frequency=frequency,
        due_date=due,
    )
    pet_obj.add_task(new_task)
    st.success(f"Added '{task_title}' for {task_pet}")

# Show current task table
all_tasks_data = []
for p in st.session_state.pets:
    for t in p.tasks:
        all_tasks_data.append({
            "Pet": t.pet_name,
            "Task": t.title,
            "Time": t.scheduled_time or "flex",
            "Duration": f"{t.duration_minutes} min",
            "Priority": t.priority,
            "Category": t.category,
            "Frequency": t.frequency,
        })

if all_tasks_data:
    st.table(all_tasks_data)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# ---- Step 3: Generate schedule --------------------------------------------

st.subheader("3. Today's Schedule")

# Build owner object for the scheduler
owner = Owner(
    name=owner_name,
    pets=st.session_state.pets,
    available_minutes=int(available_minutes),
)

scheduler = Scheduler(owner)

# Filter controls
st.markdown("**Filter tasks**")
fcol1, fcol2 = st.columns(2)
with fcol1:
    filter_pet = st.selectbox("Filter by pet", ["All"] + pet_names)
with fcol2:
    filter_cat = st.selectbox(
        "Filter by category",
        ["All", "walk", "feed", "medicine", "grooming", "enrichment", "other"],
    )

if st.button("Generate schedule", type="primary"):
    # Conflict warnings
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for w in conflicts:
            st.warning(f"⚠️ {w}")

    # Generate
    schedule = scheduler.generate_schedule()

    if not schedule:
        st.info("No tasks to schedule. Add some tasks above!")
    else:
        # Apply display filters
        display = schedule
        if filter_pet != "All":
            display = [t for t in display if t.pet_name == filter_pet]
        if filter_cat != "All":
            display = [t for t in display if t.category == filter_cat]

        # Schedule table
        schedule_data = []
        for i, t in enumerate(display, 1):
            time_str = t.scheduled_time if t.scheduled_time else "flex"
            freq_str = f" ({t.frequency})" if t.frequency != "once" else ""
            schedule_data.append({
                "#": i,
                "Time": time_str,
                "Task": f"{t.title}{freq_str}",
                "Pet": t.pet_name,
                "Duration": f"{t.duration_minutes} min",
                "Priority": t.priority.upper(),
            })
        st.table(schedule_data)

        # Explanation
        with st.expander("Why this order?"):
            st.text(scheduler.explain_plan(schedule))

        # Stats
        total = sum(t.duration_minutes for t in schedule)
        remaining = int(available_minutes) - total
        st.success(
            f"Scheduled {len(schedule)} tasks using {total}/{int(available_minutes)} minutes. "
            f"{remaining} minutes remaining."
        )

        # Skipped tasks
        all_pending = [t for t in scheduler.tasks if not t.completed]
        skipped = [t for t in all_pending if t not in schedule]
        if skipped:
            st.warning(
                "Skipped (not enough time): "
                + ", ".join(f"{t.title} ({t.pet_name})" for t in skipped)
            )
