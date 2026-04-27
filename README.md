# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

---

## 🐾 Smarter Scheduling Features (Phase 2)

PawPal+ now includes intelligent scheduling algorithms that go beyond simple task lists:

### **1. Priority + Time Sorting** ⭐
- **What it does:** Tasks are sorted by priority level first (High → Medium → Low), then chronologically
- **Why it matters:** Pet owners see urgent tasks first, but within each tier tasks flow naturally by time
- **Method:** `sortTasksByPriority(tasks)` uses multi-key tuple sorting

### **2. Intelligent Conflict Detection** 🚨
- **What it does:** Prevents overlapping walks for the same pet using time-range overlap detection
- **Algorithm:** Checks if `new_start < existing_end AND new_end > existing_start`
- **Tradeoff:** Rejects conflicts outright (no manual override) for guaranteed correctness
- **Methods:** `hasConflict()` for single checks, `checkAllConflicts()` for full validation

### **3. Recurring Task Automation** 🔄
- **What it does:** Daily/weekly tasks automatically spawn new instances when completed
- **How it works:** When "Feed Buddy" (daily) is marked done, tomorrow's feeding is auto-created
- **Implementation:** Uses `timedelta(days=1)` or `timedelta(weeks=1)` for date math
- **Methods:** `createRecurringTask()` to initialize, `completeTask()` to expand

### **4. Smart Filtering** 🎯
- **By Pet:** `getTasksByPetName()` — quickly see all tasks for one pet
- **By Status:** `getTasksByStatus()` — separate pending from completed tasks
- **By Priority:** `getTasksByPriority()` — focus on urgent work first
- **Dashboard View:** `getOrganizedTodaysTasks()` — nested dict for multi-pet households

### **5. Comprehensive Scheduling Reports**
- **Today's Schedule:** `getOrganizedTodaysTasks()` shows all pending tasks grouped by pet, sorted by urgency
- **Conflict Audits:** `checkAllConflicts()` validates entire schedule for impossible overlaps
- **Status Summary:** `getPendingTasks()` and `getTasksByStatus()` track work progress

### Example Usage

```python
from pawpal_system import User, Pet, Scheduler
from datetime import datetime, timedelta

# Setup
user = User(userId="u1", name="Malik", email="malik@pawpal.com")
dog = Pet(petId="p1", name="Buddy", breed="Golden", age=3)
user.addPet(dog)
scheduler = Scheduler(user)

# Create a recurring daily task
today = datetime.now()
morning = today.replace(hour=8, minute=0)
scheduler.createRecurringTask(dog, "Feed Buddy", morning, "high", recurrence="daily")

# Schedule walks with conflict detection
walk_time = today.replace(hour=9, minute=0)
scheduler.scheduleWalk(dog, walk_time, 30)

# View organized schedule
schedule = scheduler.getOrganizedTodaysTasks()
for pet_name, tasks in schedule.items():
    print(f"🐾 {pet_name}")
    for task in tasks:
        print(f"  {task.dueDate.strftime('%H:%M')} - {task.description}")
```

### Testing

Run the test suite to verify algorithm correctness:

```bash
pytest tests/test_pawpal.py -v
```

Key test categories:
- **Task Completion:** Mark complete & expand recurring tasks
- **Conflict Detection:** Overlapping vs. non-overlapping walks
- **Sorting:** Priority-based + time-based ordering
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.


Testing PawPal+
Sorting Correctness (5 tests) – Validates that tasks are ordered by priority first, then by time.

test_sort_by_time_chronological_order – Verifies morning tasks appear before afternoon tasks regardless of input order.

test_sort_by_priority_high_first – Confirms high-priority tasks come before medium/low even if scheduled later.

test_sort_priority_same_time_different_priorities – Ensures priority wins as the tiebreaker when times are identical.

test_sort_empty_list – Tests that sorting an empty list returns an empty list without crashing.

test_sort_single_task – Validates that a single task list remains intact after sorting.

Recurring Task Logic (5 tests) – Ensures daily/weekly tasks automatically create next occurrences when marked complete.

test_daily_task_creates_next_day_occurrence – Confirms completing a task at 8 AM creates a new task for tomorrow at 8 AM.

test_weekly_task_creates_next_week_occurrence – Verifies weekly tasks expand exactly 7 days into the future.

test_one_time_task_no_expansion – Ensures one-time tasks do not create new instances when completed.

test_recurring_task_chain – Tests that recurring tasks can be completed multiple times, each generating the next occurrence.

test_recurring_expansion_preserves_metadata – Confirms expanded tasks retain description, priority, pet, and recurrence type.

Conflict Detection (10 tests) – Validates the scheduler prevents overlapping walks and catches impossible schedules.

test_conflict_identical_times – Ensures two walks at the exact same time are flagged as conflicts.

test_conflict_overlapping_walks – Detects when a walk at 8:15 AM overlaps with an existing 8:00–8:30 AM walk.

test_no_conflict_back_to_back_walks – Allows walks that start exactly when another ends (8:30 to 8:30 transition).

test_no_conflict_gap_between_walks – Permits walks with a gap between them without flagging conflicts.

test_conflict_with_completed_walks_ignored – Completed walks don't block new scheduling at the same time.

test_no_conflict_different_pets – Allows simultaneous walks for different pets without conflict detection.

test_conflict_partial_overlap_start – Catches overlaps at the beginning of a scheduled walk window.

test_conflict_partial_overlap_end – Catches overlaps at the end of a scheduled walk window.

test_check_all_conflicts_empty_schedule – Returns an empty conflict list when no overlaps exist.

test_check_all_conflicts_detects_all – Scans the entire schedule and reports all detected conflicts.

Filtering Logic (5 tests) – Verifies tasks can be filtered by pet name and completion status.

test_filter_by_pet_name – Returns only tasks for the specified pet, excluding other pets' tasks.

test_filter_by_pet_name_case_insensitive – Ensures filtering works regardless of uppercase or lowercase input.

test_filter_by_completion_status_pending – Returns only uncompleted tasks when filtering for pending items.

test_filter_by_completion_status_completed – Returns only finished tasks when filtering for completed items.
