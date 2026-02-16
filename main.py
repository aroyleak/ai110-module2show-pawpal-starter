from pawpal_system import User, Pet, Task, Walk, Scheduler
from datetime import datetime, timedelta

# Create a User (Owner)
user = User(
    userId="user_001",
    name="Malik",
    email="malik@pawpal.com"
)

# Create two Pets
dog = Pet(
    petId="pet_001",
    name="Buddy",
    breed="Golden Retriever",
    age=3
)

cat = Pet(
    petId="pet_002",
    name="Whiskers",
    breed="Siamese",
    age=2
)

# Add pets to user
user.addPet(dog)
user.addPet(cat)

# Create a Scheduler
scheduler = Scheduler(user)

# Schedule walks and tasks for today (OUT OF ORDER to test sorting)
today = datetime.now()
morning_time = today.replace(hour=8, minute=0, second=0, microsecond=0)
afternoon_time = today.replace(hour=14, minute=0, second=0, microsecond=0)
evening_time = today.replace(hour=18, minute=0, second=0, microsecond=0)
noon_time = today.replace(hour=12, minute=0, second=0, microsecond=0)

# Add tasks OUT OF ORDER to test sorting
# Evening task first
feed_task = Task(
    taskId="task_feeding_001",
    description="Feed Buddy dinner",
    dueDate=evening_time,
    priority="high",
    user=user,
    pet=dog
)
user.tasks.append(feed_task)
dog.tasks.append(feed_task)

# Morning walk (should be first chronologically)
scheduler.scheduleWalk(dog, morning_time, 30)

# Afternoon walk for cat
scheduler.scheduleWalk(cat, afternoon_time, 15)

# Noon task (medium priority, between times)
noon_task = Task(
    taskId="task_play_001",
    description="Play with Whiskers",
    dueDate=noon_time,
    priority="medium",
    user=user,
    pet=cat
)
user.tasks.append(noon_task)
cat.tasks.append(noon_task)

# Mark one task as complete to test filtering
feed_task.markComplete()

# Print Today's Schedule
print("=" * 60)
print(f"TODAY'S SCHEDULE FOR {user.name}".center(60))
print("=" * 60)

organized_tasks = scheduler.getOrganizedTodaysTasks()

for pet_name, tasks in organized_tasks.items():
    print(f"\n🐾 {pet_name.upper()}")
    print("-" * 60)
    for task in tasks:  # Already sorted by priority + time
        status = "✓" if task.isCompleted else "○"
        time_str = task.dueDate.strftime("%I:%M %p")
        priority_icon = "🔴" if task.priority == "high" else "🟡" if task.priority == "medium" else "🟢"
        print(f"{status} {time_str} - {task.description} {priority_icon}")

print("\n" + "=" * 60)
print(f"Total tasks today: {len(scheduler.user.getTodaysTasks())}")
print("=" * 60)

# FILTERING & SORTING TESTS
print("\n\n" + "=" * 60)
print("FILTERING TESTS".center(60))
print("=" * 60)

# Test 1: Filter by pet name
print("\n📌 Tasks for BUDDY only:")
buddy_tasks = scheduler.getTasksByPetName("Buddy")
for task in scheduler.sortTasksByTime(buddy_tasks):
    time_str = task.dueDate.strftime("%I:%M %p")
    status = "✓" if task.isCompleted else "○"
    print(f"  {status} {time_str} - {task.description}")

# Test 2: Filter by pet name (cat)
print("\n📌 Tasks for WHISKERS only:")
whiskers_tasks = scheduler.getTasksByPetName("Whiskers")
for task in scheduler.sortTasksByTime(whiskers_tasks):
    time_str = task.dueDate.strftime("%I:%M %p")
    status = "✓" if task.isCompleted else "○"
    print(f"  {status} {time_str} - {task.description}")

# Test 3: Filter by completion status (pending)
print("\n📌 All PENDING tasks (sorted by priority + time):")
pending_tasks = scheduler.getPendingTasks()
for task in scheduler.sortTasksByPriority(pending_tasks):
    time_str = task.dueDate.strftime("%I:%M %p")
    pet_name = task.pet.name if task.pet else "N/A"
    priority_icon = "🔴" if task.priority == "high" else "🟡" if task.priority == "medium" else "🟢"
    print(f"  ○ {time_str} - [{pet_name}] {task.description} {priority_icon}")

# Test 4: Filter by completion status (completed)
print("\n📌 All COMPLETED tasks:")
completed_tasks = scheduler.getTasksByStatus(completed=True)
if completed_tasks:
    for task in completed_tasks:
        time_str = task.dueDate.strftime("%I:%M %p")
        pet_name = task.pet.name if task.pet else "N/A"
        print(f"  ✓ {time_str} - [{pet_name}] {task.description}")
else:
    print("  No completed tasks yet.")

# CONFLICT DETECTION TESTS
print("\n\n" + "=" * 60)
print("CONFLICT DETECTION TESTS".center(60))
print("=" * 60)

# Test 1: Schedule a valid walk with no conflict
print("\n📌 Test 1: Schedule first walk (should succeed)")
first_walk_time = today.replace(hour=9, minute=0, second=0, microsecond=0)
scheduler.scheduleWalk(dog, first_walk_time, 30)

# Test 2: Schedule overlapping walk (should be rejected)
print("\n📌 Test 2: Schedule overlapping walk (should fail)")
overlapping_time = today.replace(hour=9, minute=15, second=0, microsecond=0)
scheduler.scheduleWalk(dog, overlapping_time, 30)

# Test 3: Schedule walk after first one ends (should succeed)
print("\n📌 Test 3: Schedule walk after first one ends (should succeed)")
valid_time = today.replace(hour=10, minute=0, second=0, microsecond=0)
scheduler.scheduleWalk(dog, valid_time, 20)

# Test 4: Check all conflicts in the schedule
print("\n📌 Test 4: Check all conflicts in schedule")
all_conflicts = scheduler.checkAllConflicts()
if all_conflicts:
    print("\n".join(all_conflicts))
else:
    print("✅ No conflicts detected in the entire schedule!")

# Create recurring daily task
print("\n\n" + "=" * 60)
print("RECURRING TASK TEST".center(60))
print("=" * 60)

feed_time = today.replace(hour=8, minute=0, second=0, microsecond=0)

daily_feed_task = scheduler.createRecurringTask(
    pet=dog,
    description="Feed Buddy (breakfast)",
    start_time=feed_time,
    priority="high",
    recurrence="daily"
)

print(f"\n📌 Created daily task: {daily_feed_task.description}")
print(f"   Due: {daily_feed_task.dueDate.strftime('%Y-%m-%d %I:%M %p')}")
print(f"   Recurrence: {daily_feed_task.recurrence}")

# Simulate completing the task
print(f"\n✓ Marking '{daily_feed_task.description}' as complete...")
next_task = scheduler.completeTask(daily_feed_task)

if next_task:
    print(f"✅ New occurrence created!")
    print(f"   Task ID: {next_task.taskId}")
    print(f"   Due: {next_task.dueDate.strftime('%Y-%m-%d %I:%M %p')}")
    print(f"   Days ahead: {(next_task.dueDate.date() - today.date()).days}")
else:
    print("❌ No new occurrence created.")