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
