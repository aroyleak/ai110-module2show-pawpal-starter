# PawPal+ System: Core Behaviors Verification Checklist

## Overview
This document lists 5 critical behaviors that should be verified to ensure the scheduling system works correctly. Each behavior is mapped to test cases and implementation details.

---

## 1. ✅ Task Sorting by Priority + Time

### Behavior:
Tasks should be sorted first by priority (high → medium → low), then chronologically within each priority tier.

### Why It Matters:
Owners need to see urgent tasks first, but within each urgency level, tasks should flow naturally by time of day.

### Test Cases:
```python
def test_sort_tasks_by_priority():
    """Verify tasks appear in priority order first, time second."""
    
    # Setup: Create 3 tasks with mixed priorities and times
    task_high_8am = Task(..., priority="high", dueDate=8:00)
    task_low_7am = Task(..., priority="low", dueDate=7:00)
    task_medium_9am = Task(..., priority="medium", dueDate=9:00)
    
    # Execute
    sorted_tasks = scheduler.sortTasksByPriority([
        task_low_7am, task_high_8am, task_medium_9am
    ])
    
    # Verify
    assert sorted_tasks[0].priority == "high"      # High first, despite later time
    assert sorted_tasks[1].priority == "medium"    # Medium second
    assert sorted_tasks[2].priority == "low"       # Low last, despite earlier time
```

### Implementation:
- **File:** `pawpal_system.py`, line 290–300
- **Method:** `Scheduler.sortTasksByPriority()`
- **Algorithm:** Tuple-based sorting with `(priority_order, dueDate)` as key
- **Data Structure:** Lambda function with dictionary lookup

### Expected Output:
```
Task 1: Feed Buddy (high priority, 8:00 AM)
Task 2: Play with Whiskers (medium priority, 9:00 AM)
Task 3: Grooming (low priority, 7:00 AM)
```

---

## 2. ⚠️ Conflict Detection (Time Range Overlap)

### Behavior:
The system should detect when two walks for the same pet overlap in time and prevent the conflicting walk from being scheduled.

### Why It Matters:
A pet cannot physically be walked at two different times simultaneously. The overlap detection must account for walk duration, not just start times.

### Test Cases:
```python
def test_no_conflict_for_non_overlapping_walks():
    """Verify non-overlapping walks pass conflict check."""
    
    # Walk 1: 8:00–8:30 (30 min)
    scheduler.scheduleWalk(dog, time=8:00, duration=30)
    
    # Walk 2: 8:30–9:00 (no overlap, back-to-back is OK)
    has_conflict, msg = scheduler.hasConflict(dog, time=8:30, duration=30)
    assert has_conflict is False

def test_conflict_for_overlapping_walks():
    """Verify overlapping walks are detected."""
    
    # Walk 1: 8:00–8:30
    scheduler.scheduleWalk(dog, time=8:00, duration=30)
    
    # Walk 2: 8:15–8:45 (OVERLAPS! 8:15–8:30 is shared)
    has_conflict, msg = scheduler.hasConflict(dog, time=8:15, duration=30)
    assert has_conflict is True
    assert "CONFLICT" in msg

def test_conflict_partial_overlap():
    """Verify partial overlaps are detected."""
    
    # Walk 1: 8:00–8:45
    scheduler.scheduleWalk(dog, time=8:00, duration=45)
    
    # Walk 2: 8:30–9:00 (overlaps 8:30–8:45)
    has_conflict, msg = scheduler.hasConflict(dog, time=8:30, duration=30)
    assert has_conflict is True
```

### Implementation:
- **File:** `pawpal_system.py`, line 380–420
- **Method:** `Scheduler.hasConflict(pet, scheduled_time, duration)`
- **Algorithm:** Mathematical overlap detection:
  ```
  new_end = new_start + duration
  existing_end = existing_start + duration
  
  Overlap if: new_start < existing_end AND new_end > existing_start
  ```
- **Return Value:** Tuple `(bool, str)` — (has_conflict, message)

### Expected Output:
```
✅ No conflicts found for Buddy at 08:30 AM
or
⚠️  CONFLICT: Buddy already has 'Walk Buddy' at 08:00 AM (duration: 30 min)
```

### Edge Cases to Verify:
- ✅ Back-to-back walks (8:30 start when previous ends at 8:30) — should NOT conflict
- ✅ Partial overlaps — should detect
- ✅ Exact same time — should detect
- ✅ Tasks without walk data — should skip

---

## 3. 🔄 Recurring Task Auto-Expansion

### Behavior:
When a recurring task (daily/weekly) is marked complete, a new instance should automatically be created for the next occurrence.

### Why It Matters:
Eliminates repetitive manual task creation for routine pet care (feeding, medication, etc.).

### Test Cases:
```python
def test_daily_task_expands_on_completion():
    """Verify daily task creates next day's instance."""
    
    # Create daily feeding task for Feb 15
    today = datetime(2026, 2, 15, 8, 0)
    daily_feed = scheduler.createRecurringTask(
        dog, 
        "Feed Buddy", 
        today, 
        "high", 
        recurrence="daily"
    )
    initial_count = len(scheduler.user.tasks)
    assert daily_feed.recurrence == "daily"
    
    # Mark as complete
    next_task = scheduler.completeTask(daily_feed)
    
    # Verify
    assert daily_feed.isCompleted is True
    assert next_task is not None
    assert next_task.dueDate == datetime(2026, 2, 16, 8, 0)  # +1 day
    assert len(scheduler.user.tasks) == initial_count + 1
    assert next_task.recurrence == "daily"

def test_weekly_task_expands_on_completion():
    """Verify weekly task creates next week's instance."""
    
    # Create weekly grooming task
    today = datetime(2026, 2, 15, 14, 0)
    weekly_groom = scheduler.createRecurringTask(
        dog,
        "Groom Buddy",
        today,
        "medium",
        recurrence="weekly"
    )
    
    # Mark as complete
    next_task = scheduler.completeTask(weekly_groom)
    
    # Verify
    assert next_task.dueDate == datetime(2026, 2, 22, 14, 0)  # +7 days
    assert next_task.recurrence == "weekly"

def test_one_time_task_does_not_expand():
    """Verify one-time tasks don't create new instances."""
    
    # Create non-recurring task
    one_time = scheduler.createRecurringTask(
        dog,
        "Buy dog food",
        datetime.now(),
        "medium",
        recurrence=None  # No recurrence
    )
    
    # Mark as complete
    result = scheduler.completeTask(one_time)
    
    # Verify
    assert result is None  # No new task created
```

### Implementation:
- **File:** `pawpal_system.py`, line 175–210
- **Methods:** `Scheduler.completeTask()` and `Task.getNextOccurrence()`
- **Algorithm:** 
  1. Mark current task `isCompleted = True`
  2. Check `task.recurrence` field
  3. Calculate next date: `dueDate + timedelta(days=1)` or `+ timedelta(weeks=1)`
  4. Clone task with new `taskId` and `dueDate`
  5. Add to both `user.tasks` and `pet.tasks`
- **Data:** `timedelta` arithmetic ensures accurate date math

### Expected Behavior:
```
Daily task (Feb 15) → Complete → Feb 16 task created
Weekly task (Feb 15) → Complete → Feb 22 task created
One-time task → Complete → No new task
```

---

## 4. 🎯 Task Filtering by Pet & Status

### Behavior:
The system should return subsets of tasks filtered by:
- Pet name (case-insensitive)
- Completion status (completed vs. pending)
- Priority level

### Why It Matters:
Owners with multiple pets need quick access to tasks for specific pets without scrolling through everything. Status filtering helps track progress.

### Test Cases:
```python
def test_filter_tasks_by_pet_name():
    """Verify filtering returns only tasks for specified pet."""
    
    # Create tasks for two pets
    buddy_task = Task(..., pet=dog, description="Walk Buddy")
    whiskers_task = Task(..., pet=cat, description="Feed Whiskers")
    
    scheduler.user.tasks = [buddy_task, whiskers_task]
    
    # Filter by pet name
    buddy_tasks = scheduler.getTasksByPetName("Buddy")
    whiskers_tasks = scheduler.getTasksByPetName("whiskers")  # Case-insensitive
    
    # Verify
    assert len(buddy_tasks) == 1
    assert buddy_tasks[0].pet.name == "Buddy"
    assert len(whiskers_tasks) == 1
    assert whiskers_tasks[0].pet.name == "Whiskers"

def test_filter_tasks_by_status():
    """Verify filtering separates completed from pending."""
    
    # Create mixed tasks
    completed = Task(..., isCompleted=True, description="Completed walk")
    pending = Task(..., isCompleted=False, description="Pending walk")
    
    scheduler.user.tasks = [completed, pending]
    
    # Filter by status
    done = scheduler.getTasksByStatus(completed=True)
    todo = scheduler.getTasksByStatus(completed=False)
    
    # Verify
    assert len(done) == 1
    assert done[0].isCompleted is True
    assert len(todo) == 1
    assert todo[0].isCompleted is False

def test_get_pending_tasks():
    """Verify convenience method returns only uncompleted tasks."""
    
    scheduler.user.tasks = [
        Task(..., isCompleted=True),
        Task(..., isCompleted=False),
        Task(..., isCompleted=False),
    ]
    
    pending = scheduler.getPendingTasks()
    assert len(pending) == 2
```

### Implementation:
- **File:** `pawpal_system.py`, line 320–360
- **Methods:**
  - `getTasksByPetName(pet_name: str)` — Case-insensitive string match
  - `getTasksByStatus(completed: bool)` — Boolean filter
  - `getPendingTasks()` — Convenience for `getTasksByStatus(False)`
- **Pattern:** List comprehensions with simple predicates

### Expected Output:
```
Buddy's tasks: [Walk, Feed, Medication]
Whiskers's tasks: [Feed, Play]
Pending: 5 tasks
Completed: 2 tasks
```

---

## 5. 📊 Organized Daily Schedule (Multi-Pet View)

### Behavior:
The system should return today's tasks organized in a nested dictionary structure:
- **Grouped by pet name** (top level)
- **Sorted by priority + time** within each pet's list

### Why It Matters:
Multi-pet households need a clear per-pet breakdown of the daily agenda, with urgent tasks visually prioritized.

### Test Cases:
```python
def test_organized_todays_tasks():
    """Verify today's tasks are grouped by pet and sorted by priority+time."""
    
    # Create today's tasks (mixed order)
    task_1 = Task(pet=dog, description="Walk", priority="high", dueDate=today_9am)
    task_2 = Task(pet=cat, description="Feed", priority="medium", dueDate=today_8am)
    task_3 = Task(pet=dog, description="Feed", priority="medium", dueDate=today_8am)
    task_4 = Task(pet=cat, description="Play", priority="low", dueDate=today_10am)
    
    scheduler.user.tasks = [task_1, task_2, task_3, task_4]
    
    # Get organized schedule
    organized = scheduler.getOrganizedTodaysTasks()
    
    # Verify structure
    assert "Buddy" in organized
    assert "Whiskers" in organized
    assert len(organized["Buddy"]) == 2
    assert len(organized["Whiskers"]) == 2
    
    # Verify Buddy's tasks are sorted: high priority (walk at 9am) before medium (feed at 8am)
    buddy_tasks = organized["Buddy"]
    assert buddy_tasks[0].priority == "high"
    assert buddy_tasks[1].priority == "medium"
    
    # Verify Whiskers' tasks: medium (8am) before low (10am)
    whiskers_tasks = organized["Whiskers"]
    assert whiskers_tasks[0].priority == "medium"
    assert whiskers_tasks[1].priority == "low"
```

### Implementation:
- **File:** `pawpal_system.py`, line 305–318
- **Method:** `Scheduler.getOrganizedTodaysTasks()`
- **Algorithm:**
  1. Get all pending tasks for today (`getTodaysTasks()`)
  2. Group by `task.pet.name` into dictionary
  3. For each pet's task list, apply `sortTasksByPriority()`
  4. Return nested dict structure
- **Return Type:** `dict[str, List[Task]]`

### Expected Output:
```python
{
    "Buddy": [
        Task("Walk Buddy", priority="high", 9:00),
        Task("Feed Buddy", priority="medium", 8:00)
    ],
    "Whiskers": [
        Task("Feed Whiskers", priority="medium", 8:00),
        Task("Play with Whiskers", priority="low", 10:00)
    ]
}
```

### Edge Cases to Verify:
- ✅ Multiple pets with different task counts
- ✅ Tasks without pet assigned (should go to "General")
- ✅ Only completed tasks (should return empty)
- ✅ Mixed priorities within same pet

---

## Summary Table

| Behavior | Method(s) | Critical Test | Pass/Fail |
|----------|-----------|---------------|-----------|
| 1. Priority + Time Sorting | `sortTasksByPriority()` | High priority before low, even if low time is earlier | ❓ |
| 2. Conflict Detection | `hasConflict()`, `scheduleWalk()` | Overlapping walks detected; back-to-back walks OK | ❓ |
| 3. Recurring Task Expansion | `completeTask()`, `createRecurringTask()` | Daily task creates next day; weekly creates next week; one-time doesn't expand | ❓ |
| 4. Task Filtering | `getTasksByPetName()`, `getTasksByStatus()`, `getPendingTasks()` | Case-insensitive pet names; status separated correctly | ❓ |
| 5. Organized Daily View | `getOrganizedTodaysTasks()` | Tasks grouped by pet, sorted by priority+time within each group | ❓ |

---

## Running Verification Tests

```bash
# Run all tests
pytest tests/test_pawpal.py -v

# Run specific behavior
pytest tests/test_pawpal.py::TestTaskSorting -v
pytest tests/test_pawpal.py::TestConflictDetection -v
pytest tests/test_pawpal.py::TestRecurringTasks -v
pytest tests/test_pawpal.py::TestTaskFiltering -v
pytest tests/test_pawpal.py::TestScheduleOrganization -v
```

---

## Notes

- **Behavior 2 (Conflict Detection)** is the most complex; prioritize this first
- **Behavior 3 (Recurring Tasks)** depends on accurate `timedelta` arithmetic
- **Behavior 4 & 5** are simpler list operations but critical for UX
- All behaviors should handle edge cases (empty lists, None values, duplicate names)

---

*Verification checklist created: February 15, 2026*
