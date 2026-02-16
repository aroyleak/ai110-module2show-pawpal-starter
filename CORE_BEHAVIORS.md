# 5 Core Behaviors: Quick Reference

## 1️⃣ Task Sorting by Priority + Time ⭐
**What:** Tasks sorted high → medium → low, then by time  
**Method:** `sortTasksByPriority(tasks)`  
**Example:**
```
Input:  [Low 7am, High 8am, Medium 9am]
Output: [High 8am, Medium 9am, Low 7am]  ← Priority wins, not time
```
**Test:** High priority task at 8am appears before low priority task at 7am

---

## 2️⃣ Conflict Detection (Overlap) 🚨
**What:** Prevent overlapping walks for same pet  
**Method:** `hasConflict(pet, time, duration)`  
**Algorithm:** `new_start < existing_end AND new_end > existing_start`  
**Example:**
```
Existing walk: 8:00–8:30
New walk:      8:15–8:45
Result:        ⚠️  CONFLICT (overlap 8:15–8:30)

New walk:      8:30–9:00
Result:        ✅ OK (back-to-back is allowed)
```
**Test:** Must detect partial overlaps, not just exact time matches

---

## 3️⃣ Recurring Task Auto-Expansion 🔄
**What:** Complete daily/weekly task → next instance auto-created  
**Methods:** `createRecurringTask()` + `completeTask()`  
**Example:**
```
Feb 15: Create "Feed Buddy" (daily, 8:00 AM)
        → markComplete()
        → Automatically create "Feed Buddy" for Feb 16 at 8:00 AM
        
Feb 22: Create "Grooming" (weekly, 2:00 PM)
        → markComplete()
        → Automatically create "Grooming" for Mar 1 at 2:00 PM
```
**Test:** Daily tasks increment by 1 day; weekly by 7 days; one-time tasks don't expand

---

## 4️⃣ Task Filtering (Pet & Status) 🎯
**What:** Quickly find tasks by pet name or completion status  
**Methods:**
- `getTasksByPetName("Buddy")` — Case-insensitive  
- `getTasksByStatus(completed=False)` — Pending tasks only  
- `getPendingTasks()` — Shortcut for above  
**Example:**
```
All tasks: [Walk Buddy, Feed Whiskers, Groom Buddy, Play Whiskers]

getTasksByPetName("Buddy"):
  → [Walk Buddy, Groom Buddy]

getTasksByStatus(completed=False):
  → [Walk Buddy, Feed Whiskers, Groom Buddy, Play Whiskers]

getTasksByStatus(completed=True):
  → []
```
**Test:** Pet name matching is case-insensitive; status filtering is exact

---

## 5️⃣ Organized Daily Schedule (Multi-Pet) 📊
**What:** Today's tasks grouped by pet, sorted by priority+time per pet  
**Method:** `getOrganizedTodaysTasks()`  
**Example:**
```python
{
    "Buddy": [
        "Walk Buddy" (HIGH, 9:00 AM),
        "Feed Buddy" (MEDIUM, 8:00 AM)
    ],
    "Whiskers": [
        "Feed Whiskers" (MEDIUM, 8:00 AM),
        "Play Whiskers" (LOW, 10:00 AM)
    ]
}
```
**Structure:** `dict[pet_name: str] → list[tasks sorted by priority+time]`  
**Test:** Each pet's tasks are grouped AND sorted; high priority first within each pet

---

## Implementation Status

| Behavior | Line# | Status | Notes |
|----------|-------|--------|-------|
| 1. Sorting | 290–300 | ✅ Complete | Tuple-based lambda key |
| 2. Conflict Detection | 380–420 | ✅ Complete | Overlap formula implemented |
| 3. Recurring Expansion | 175–210 | ✅ Complete | timedelta arithmetic |
| 4. Filtering | 320–360 | ✅ Complete | List comprehensions |
| 5. Organized View | 305–318 | ✅ Complete | Nested dict structure |

---

## Run Verification

```bash
pytest tests/test_pawpal.py -v
```

Expected: All 5 behaviors should pass their respective test cases.

---

*Quick reference guide • February 15, 2026*
