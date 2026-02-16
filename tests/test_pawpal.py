import pytest
import sys
from pathlib import Path

# Add parent directory to path so we can import pawpal_system
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timedelta
from pawpal_system import User, Pet, Task, Walk, Scheduler


class TestSortingCorrectness:
    """Verify that sorting logic returns tasks in correct order."""
    
    def setup_method(self):
        """Set up test fixtures before each test."""
        self.user = User(userId="user_001", name="TestOwner", email="test@pawpal.com")
        self.dog = Pet(petId="pet_001", name="Buddy", breed="Golden Retriever", age=3)
        self.user.addPet(self.dog)
        self.scheduler = Scheduler(self.user)
        self.today = datetime.now()
    
    def test_sort_by_time_chronological_order(self):
        """Verify tasks are returned in chronological order by dueDate."""
        # Arrange: Create tasks in reverse time order
        evening_task = Task(
            taskId="task_001",
            description="Feed dinner",
            dueDate=self.today.replace(hour=18, minute=0, second=0, microsecond=0),
            priority="high",
            user=self.user,
            pet=self.dog
        )
        morning_task = Task(
            taskId="task_002",
            description="Morning walk",
            dueDate=self.today.replace(hour=8, minute=0, second=0, microsecond=0),
            priority="high",
            user=self.user,
            pet=self.dog
        )
        noon_task = Task(
            taskId="task_003",
            description="Lunch",
            dueDate=self.today.replace(hour=12, minute=0, second=0, microsecond=0),
            priority="high",
            user=self.user,
            pet=self.dog
        )
        
        # Act: Sort by time
        tasks = [evening_task, morning_task, noon_task]
        sorted_tasks = self.scheduler.sortTasksByTime(tasks)
        
        # Assert: Morning → Noon → Evening
        assert sorted_tasks[0].dueDate.hour == 8
        assert sorted_tasks[1].dueDate.hour == 12
        assert sorted_tasks[2].dueDate.hour == 18
    
    def test_sort_by_priority_high_first(self):
        """Verify high priority tasks appear before medium/low when sorting by priority."""
        # Arrange
        low_task = Task(
            taskId="task_001",
            description="Optional grooming",
            dueDate=self.today.replace(hour=8, minute=0),
            priority="low",
            user=self.user,
            pet=self.dog
        )
        high_task = Task(
            taskId="task_002",
            description="Emergency vet visit",
            dueDate=self.today.replace(hour=10, minute=0),
            priority="high",
            user=self.user,
            pet=self.dog
        )
        medium_task = Task(
            taskId="task_003",
            description="Regular walk",
            dueDate=self.today.replace(hour=9, minute=0),
            priority="medium",
            user=self.user,
            pet=self.dog
        )
        
        # Act
        tasks = [low_task, high_task, medium_task]
        sorted_tasks = self.scheduler.sortTasksByPriority(tasks)
        
        # Assert: High → Medium → Low (regardless of original time order)
        assert sorted_tasks[0].priority == "high"
        assert sorted_tasks[1].priority == "medium"
        assert sorted_tasks[2].priority == "low"
    
    def test_sort_priority_same_time_different_priorities(self):
        """Verify priority wins when times are identical."""
        # Arrange: All tasks at same time, different priorities
        high_8am = Task(
            taskId="task_001",
            description="Important",
            dueDate=self.today.replace(hour=8, minute=0),
            priority="high",
            user=self.user,
            pet=self.dog
        )
        low_8am = Task(
            taskId="task_002",
            description="Optional",
            dueDate=self.today.replace(hour=8, minute=0),
            priority="low",
            user=self.user,
            pet=self.dog
        )
        medium_8am = Task(
            taskId="task_003",
            description="Normal",
            dueDate=self.today.replace(hour=8, minute=0),
            priority="medium",
            user=self.user,
            pet=self.dog
        )
        
        # Act
        tasks = [low_8am, high_8am, medium_8am]
        sorted_tasks = self.scheduler.sortTasksByPriority(tasks)
        
        # Assert: High comes first, even though all have same time
        assert sorted_tasks[0].priority == "high"
        assert sorted_tasks[1].priority == "medium"
        assert sorted_tasks[2].priority == "low"
    
    def test_sort_empty_list(self):
        """Sorting an empty list should return empty list."""
        # Act
        sorted_tasks = self.scheduler.sortTasksByTime([])
        
        # Assert
        assert sorted_tasks == []
    
    def test_sort_single_task(self):
        """Sorting a single task should return a list with that task."""
        # Arrange
        single_task = Task(
            taskId="task_001",
            description="Solo task",
            dueDate=self.today.replace(hour=8, minute=0),
            priority="high",
            user=self.user,
            pet=self.dog
        )
        
        # Act
        sorted_tasks = self.scheduler.sortTasksByTime([single_task])
        
        # Assert
        assert len(sorted_tasks) == 1
        assert sorted_tasks[0] == single_task


class TestRecurrenceLogic:
    """Verify that recurring tasks expand correctly."""
    
    def setup_method(self):
        """Set up test fixtures before each test."""
        self.user = User(userId="user_001", name="TestOwner", email="test@pawpal.com")
        self.dog = Pet(petId="pet_001", name="Buddy", breed="Golden Retriever", age=3)
        self.user.addPet(self.dog)
        self.scheduler = Scheduler(self.user)
        self.today = datetime.now()
    
    def test_daily_task_creates_next_day_occurrence(self):
        """Verify marking a daily task complete creates a new task for tomorrow."""
        # Arrange
        morning_time = self.today.replace(hour=8, minute=0, second=0, microsecond=0)
        daily_task = self.scheduler.createRecurringTask(
            pet=self.dog,
            description="Feed Buddy (breakfast)",
            start_time=morning_time,
            priority="high",
            recurrence="daily"
        )
        
        initial_task_count = len(self.user.tasks)
        
        # Act
        next_task = self.scheduler.completeTask(daily_task)
        
        # Assert: New task created
        assert next_task is not None
        assert len(self.user.tasks) == initial_task_count + 1
        
        # Assert: New task is tomorrow at same time
        expected_next_date = morning_time + timedelta(days=1)
        assert next_task.dueDate == expected_next_date
        
        # Assert: Original task is marked complete
        assert daily_task.isCompleted is True
        
        # Assert: New task inherits metadata
        assert next_task.description == daily_task.description
        assert next_task.priority == daily_task.priority
        assert next_task.recurrence == "daily"
    
    def test_weekly_task_creates_next_week_occurrence(self):
        """Verify marking a weekly task complete creates a new task for next week."""
        # Arrange
        grooming_time = self.today.replace(hour=10, minute=0, second=0, microsecond=0)
        weekly_task = self.scheduler.createRecurringTask(
            pet=self.dog,
            description="Weekly grooming",
            start_time=grooming_time,
            priority="medium",
            recurrence="weekly"
        )
        
        # Act
        next_task = self.scheduler.completeTask(weekly_task)
        
        # Assert: New task is 7 days later
        expected_next_date = grooming_time + timedelta(weeks=1)
        assert next_task.dueDate == expected_next_date
        
        # Assert: Same time of day preserved
        assert next_task.dueDate.hour == grooming_time.hour
        assert next_task.dueDate.minute == grooming_time.minute
    
    def test_one_time_task_no_expansion(self):
        """Verify that completing a one-time task does NOT create a new task."""
        # Arrange
        one_time_task = Task(
            taskId="task_001",
            description="Buy special food",
            dueDate=self.today.replace(hour=14, minute=0),
            priority="low",
            user=self.user,
            pet=self.dog,
            recurrence=None  # One-time task
        )
        self.user.tasks.append(one_time_task)
        self.dog.tasks.append(one_time_task)
        initial_count = len(self.user.tasks)
        
        # Act
        result = self.scheduler.completeTask(one_time_task)
        
        # Assert: No new task created
        assert result is None
        assert len(self.user.tasks) == initial_count
        assert one_time_task.isCompleted is True
    
    def test_recurring_task_chain(self):
        """Verify recurring tasks can be completed multiple times in sequence."""
        # Arrange
        feed_time = self.today.replace(hour=8, minute=0, second=0, microsecond=0)
        daily_task = self.scheduler.createRecurringTask(
            pet=self.dog,
            description="Feed breakfast",
            start_time=feed_time,
            priority="high",
            recurrence="daily"
        )
        
        # Act & Assert: Complete task, then complete the next task
        task1 = self.scheduler.completeTask(daily_task)
        assert task1 is not None
        assert task1.dueDate == feed_time + timedelta(days=1)
        
        task2 = self.scheduler.completeTask(task1)
        assert task2 is not None
        assert task2.dueDate == feed_time + timedelta(days=2)
        
        task3 = self.scheduler.completeTask(task2)
        assert task3 is not None
        assert task3.dueDate == feed_time + timedelta(days=3)
        
        # Each task should be 1 day apart
        assert (task2.dueDate - task1.dueDate).days == 1
        assert (task3.dueDate - task2.dueDate).days == 1
    
    def test_recurring_expansion_preserves_metadata(self):
        """Verify expanded tasks preserve all original metadata."""
        # Arrange
        walk_time = self.today.replace(hour=9, minute=30, second=0, microsecond=0)
        original_task = self.scheduler.createRecurringTask(
            pet=self.dog,
            description="Morning walk",
            start_time=walk_time,
            priority="high",
            recurrence="daily"
        )
        
        # Act
        next_task = self.scheduler.completeTask(original_task)
        
        # Assert: All metadata preserved
        assert next_task.description == original_task.description
        assert next_task.priority == original_task.priority
        assert next_task.pet == original_task.pet
        assert next_task.recurrence == original_task.recurrence
        assert next_task.isCompleted is False  # New task is not complete


class TestConflictDetection:
    """Verify that conflict detection flags duplicate times and overlaps."""
    
    def setup_method(self):
        """Set up test fixtures before each test."""
        self.user = User(userId="user_001", name="TestOwner", email="test@pawpal.com")
        self.dog = Pet(petId="pet_001", name="Buddy", breed="Golden Retriever", age=3)
        self.cat = Pet(petId="pet_002", name="Whiskers", breed="Siamese", age=2)
        self.user.addPet(self.dog)
        self.user.addPet(self.cat)
        self.scheduler = Scheduler(self.user)
        self.today = datetime.now()
    
    def test_conflict_identical_times(self):
        """Verify that scheduling walks at identical times is flagged as conflict."""
        # Arrange
        walk_time = self.today.replace(hour=8, minute=0, second=0, microsecond=0)
        
        # Act: Schedule first walk
        self.scheduler.scheduleWalk(self.dog, walk_time, 30)
        
        # Act: Check for conflict with identical time
        has_conflict, message = self.scheduler.hasConflict(self.dog, walk_time, 30)
        
        # Assert
        assert has_conflict is True
        assert "CONFLICT" in message
    
    def test_conflict_overlapping_walks(self):
        """Verify that overlapping walks are detected as conflicts."""
        # Arrange
        walk1_time = self.today.replace(hour=8, minute=0, second=0, microsecond=0)
        walk2_time = self.today.replace(hour=8, minute=15, second=0, microsecond=0)  # Overlaps
        
        # Act: Schedule first walk (8:00–8:30)
        self.scheduler.scheduleWalk(self.dog, walk1_time, 30)
        
        # Act: Check for conflict with overlapping time (8:15–8:45)
        has_conflict, message = self.scheduler.hasConflict(self.dog, walk2_time, 30)
        
        # Assert
        assert has_conflict is True
        assert "CONFLICT" in message
    
    def test_no_conflict_back_to_back_walks(self):
        """Verify that back-to-back walks (no gap) are allowed."""
        # Arrange
        walk1_time = self.today.replace(hour=8, minute=0, second=0, microsecond=0)
        walk2_time = self.today.replace(hour=8, minute=30, second=0, microsecond=0)  # Starts when first ends
        
        # Act: Schedule first walk (8:00–8:30)
        self.scheduler.scheduleWalk(self.dog, walk1_time, 30)
        
        # Act: Check for conflict with back-to-back time (8:30–9:00)
        has_conflict, message = self.scheduler.hasConflict(self.dog, walk2_time, 30)
        
        # Assert: No conflict (back-to-back is allowed)
        assert has_conflict is False
        assert "No conflicts" in message
    
    def test_no_conflict_gap_between_walks(self):
        """Verify that walks with a gap between them don't conflict."""
        # Arrange
        walk1_time = self.today.replace(hour=8, minute=0, second=0, microsecond=0)
        walk2_time = self.today.replace(hour=9, minute=0, second=0, microsecond=0)  # 30 min gap
        
        # Act: Schedule first walk (8:00–8:30)
        self.scheduler.scheduleWalk(self.dog, walk1_time, 30)
        
        # Act: Check for conflict with later walk (9:00–9:30)
        has_conflict, message = self.scheduler.hasConflict(self.dog, walk2_time, 30)
        
        # Assert: No conflict
        assert has_conflict is False
    
    def test_conflict_with_completed_walks_ignored(self):
        """Verify that completed walks don't block new scheduling."""
        # Arrange
        walk_time = self.today.replace(hour=8, minute=0, second=0, microsecond=0)
        
        # Act: Schedule a walk
        walk = self.scheduler.scheduleWalk(self.dog, walk_time, 30)
        
        # Get the associated task and mark it complete
        walk_task = [t for t in self.dog.tasks if t.walk == walk][0]
        walk_task.markComplete()  # Mark task as complete (not just walk)
        
        # Act: Check if same time can be scheduled again
        has_conflict, message = self.scheduler.hasConflict(self.dog, walk_time, 30)
        
        # Assert: No conflict with completed walk
        assert has_conflict is False
        assert "No conflicts" in message
    
    def test_no_conflict_different_pets(self):
        """Verify that walks for different pets at same time don't conflict."""
        # Arrange
        walk_time = self.today.replace(hour=8, minute=0, second=0, microsecond=0)
        
        # Act: Schedule walk for dog
        self.scheduler.scheduleWalk(self.dog, walk_time, 30)
        
        # Act: Check conflict for cat at same time
        has_conflict, message = self.scheduler.hasConflict(self.cat, walk_time, 30)
        
        # Assert: No conflict (different pets can walk simultaneously)
        assert has_conflict is False
    
    def test_conflict_partial_overlap_start(self):
        """Verify that partial overlap at the start is detected."""
        # Arrange
        walk1_time = self.today.replace(hour=8, minute=0, second=0, microsecond=0)
        walk2_time = self.today.replace(hour=8, minute=20, second=0, microsecond=0)
        
        # Act: Schedule first walk (8:00–8:30)
        self.scheduler.scheduleWalk(self.dog, walk1_time, 30)
        
        # Act: Try to schedule overlapping walk (8:20–8:50)
        has_conflict, _ = self.scheduler.hasConflict(self.dog, walk2_time, 30)
        
        # Assert
        assert has_conflict is True
    
    def test_conflict_partial_overlap_end(self):
        """Verify that partial overlap at the end is detected."""
        # Arrange
        walk1_time = self.today.replace(hour=8, minute=0, second=0, microsecond=0)
        walk2_time = self.today.replace(hour=7, minute=50, second=0, microsecond=0)
        
        # Act: Schedule first walk (8:00–8:30)
        self.scheduler.scheduleWalk(self.dog, walk1_time, 30)
        
        # Act: Try to schedule overlapping walk (7:50–8:20)
        has_conflict, _ = self.scheduler.hasConflict(self.dog, walk2_time, 30)
        
        # Assert
        assert has_conflict is True
    
    def test_check_all_conflicts_empty_schedule(self):
        """Verify checkAllConflicts returns empty list for clean schedule."""
        # Act
        conflicts = self.scheduler.checkAllConflicts()
        
        # Assert
        assert conflicts == []
    
    def test_check_all_conflicts_detects_all(self):
        """Verify checkAllConflicts detects all conflicts in schedule."""
        # Arrange: Create conflicting walks
        walk_time = self.today.replace(hour=8, minute=0, second=0, microsecond=0)
        self.scheduler.scheduleWalk(self.dog, walk_time, 30)
        
        # Force a second conflicting walk directly into tasks
        conflicting_walk = Walk(
            walkId="walk_conflict",
            pet=self.dog,
            scheduledTime=walk_time,
            duration=30
        )
        conflicting_task = Task(
            taskId="task_conflict",
            description="Conflicting walk",
            dueDate=walk_time,
            priority="high",
            walk=conflicting_walk,
            pet=self.dog,
            user=self.user
        )
        self.user.tasks.append(conflicting_task)
        self.dog.tasks.append(conflicting_task)
        
        # Act
        all_conflicts = self.scheduler.checkAllConflicts()
        
        # Assert: At least one conflict detected
        assert len(all_conflicts) > 0


class TestFilteringLogic:
    """Verify filtering by status and pet name works correctly."""
    
    def setup_method(self):
        """Set up test fixtures before each test."""
        self.user = User(userId="user_001", name="TestOwner", email="test@pawpal.com")
        self.dog = Pet(petId="pet_001", name="Buddy", breed="Golden Retriever", age=3)
        self.cat = Pet(petId="pet_002", name="Whiskers", breed="Siamese", age=2)
        self.user.addPet(self.dog)
        self.user.addPet(self.cat)
        self.scheduler = Scheduler(self.user)
        self.today = datetime.now()
    
    def test_filter_by_pet_name(self):
        """Verify filtering returns only tasks for specified pet."""
        # Arrange
        dog_task = Task(
            taskId="task_001",
            description="Walk Buddy",
            dueDate=self.today.replace(hour=8, minute=0),
            priority="high",
            user=self.user,
            pet=self.dog
        )
        cat_task = Task(
            taskId="task_002",
            description="Feed Whiskers",
            dueDate=self.today.replace(hour=9, minute=0),
            priority="high",
            user=self.user,
            pet=self.cat
        )
        self.user.tasks = [dog_task, cat_task]
        
        # Act
        buddy_tasks = self.scheduler.getTasksByPetName("Buddy")
        
        # Assert
        assert len(buddy_tasks) == 1
        assert buddy_tasks[0] == dog_task
    
    def test_filter_by_pet_name_case_insensitive(self):
        """Verify pet name filtering is case-insensitive."""
        # Arrange
        dog_task = Task(
            taskId="task_001",
            description="Walk",
            dueDate=self.today.replace(hour=8, minute=0),
            priority="high",
            user=self.user,
            pet=self.dog
        )
        self.user.tasks = [dog_task]
        
        # Act
        lower = self.scheduler.getTasksByPetName("buddy")
        upper = self.scheduler.getTasksByPetName("BUDDY")
        mixed = self.scheduler.getTasksByPetName("BuDdY")
        
        # Assert: All return same result
        assert len(lower) == len(upper) == len(mixed) == 1
    
    def test_filter_by_completion_status_pending(self):
        """Verify filtering returns only pending (incomplete) tasks."""
        # Arrange
        pending_task = Task(
            taskId="task_001",
            description="Pending task",
            dueDate=self.today.replace(hour=8, minute=0),
            priority="high",
            isCompleted=False,
            user=self.user,
            pet=self.dog
        )
        completed_task = Task(
            taskId="task_002",
            description="Done task",
            dueDate=self.today.replace(hour=9, minute=0),
            priority="high",
            isCompleted=True,
            user=self.user,
            pet=self.cat
        )
        self.user.tasks = [pending_task, completed_task]
        
        # Act
        pending = self.scheduler.getPendingTasks()
        
        # Assert
        assert len(pending) == 1
        assert pending[0] == pending_task
    
    def test_filter_by_completion_status_completed(self):
        """Verify filtering returns only completed tasks."""
        # Arrange
        pending_task = Task(
            taskId="task_001",
            description="Pending",
            dueDate=self.today.replace(hour=8, minute=0),
            priority="high",
            isCompleted=False,
            user=self.user,
            pet=self.dog
        )
        completed_task = Task(
            taskId="task_002",
            description="Completed",
            dueDate=self.today.replace(hour=9, minute=0),
            priority="high",
            isCompleted=True,
            user=self.user,
            pet=self.cat
        )
        self.user.tasks = [pending_task, completed_task]
        
        # Act
        completed = self.scheduler.getCompletedTasks()
        
        # Assert
        assert len(completed) == 1
        assert completed[0] == completed_task


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

