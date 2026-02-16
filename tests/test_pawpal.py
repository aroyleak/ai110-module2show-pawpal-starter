import pytest
from datetime import datetime, timedelta
from pawpal_system import User, Pet, Task, Walk, Scheduler


class TestTaskCompletion:
    """Test that task completion works correctly."""
    
    def test_mark_complete_changes_status(self):
        """Verify that calling markComplete() changes isCompleted to True."""
        # Arrange
        task = Task(
            taskId="task_001",
            description="Walk the dog",
            dueDate=datetime.now(),
            priority="high"
        )
        
        # Act
        task.markComplete()
        
        # Assert
        assert task.isCompleted is True


class TestTaskAddition:
    """Test that adding tasks to pets works correctly."""
    
    def test_add_task_to_pet_increases_count(self):
        """Verify that adding a task to a Pet increases that pet's task count."""
        # Arrange
        pet = Pet(
            petId="pet_001",
            name="Buddy",
            breed="Golden Retriever",
            age=3
        )
        initial_count = len(pet.tasks)
        
        task = Task(
            taskId="task_001",
            description="Feed Buddy",
            dueDate=datetime.now(),
            priority="high",
            pet=pet
        )
        
        # Act
        pet.tasks.append(task)
        
        # Assert
        assert len(pet.tasks) == initial_count + 1
        assert task in pet.tasks


class TestConflictDetection:
    """Test that conflict detection works correctly."""
    
    def test_no_conflict_for_non_overlapping_walks(self):
        """Verify that non-overlapping walks are detected as safe."""
        # Arrange
        user = User(userId="user_001", name="Malik", email="malik@pawpal.com")
        pet = Pet(petId="pet_001", name="Buddy", breed="Golden Retriever", age=3)
        user.addPet(pet)
        scheduler = Scheduler(user)
        
        time1 = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
        time2 = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
        
        # Act
        scheduler.scheduleWalk(pet, time1, 30)
        has_conflict, message = scheduler.hasConflict(pet, time2, 30)
        
        # Assert
        assert has_conflict is False
    
    def test_conflict_for_overlapping_walks(self):
        """Verify that overlapping walks are detected as conflicts."""
        # Arrange
        user = User(userId="user_001", name="Malik", email="malik@pawpal.com")
        pet = Pet(petId="pet_001", name="Buddy", breed="Golden Retriever", age=3)
        user.addPet(pet)
        scheduler = Scheduler(user)
        
        time1 = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
        time2 = datetime.now().replace(hour=8, minute=15, second=0, microsecond=0)
        
        # Act
        scheduler.scheduleWalk(pet, time1, 30)
        has_conflict, message = scheduler.hasConflict(pet, time2, 30)
        
        # Assert
        assert has_conflict is True
        assert "CONFLICT" in message
    
    def hasConflict(self, pet: Pet, scheduled_time: datetime, duration: int = 30) -> tuple:
        """Check if a new task/walk conflicts with existing tasks for the same pet."""
        new_end_time = scheduled_time + timedelta(minutes=duration)
        
        def overlaps(task):
            if not task.walk:
                return False
            task_end = task.dueDate + timedelta(minutes=task.walk.duration)
            return scheduled_time < task_end and new_end_time > task.dueDate
        
        conflicts = [
            f"⚠️  CONFLICT: {pet.name} already has '{task.description}' "
            f"at {task.dueDate.strftime('%I:%M %p')} (duration: {task.walk.duration} min)"
            for task in pet.tasks if not task.isCompleted and overlaps(task)
        ]
        
        return (
            (True, "\n".join(conflicts)) if conflicts 
            else (False, f"✅ No conflicts found for {pet.name} at {scheduled_time.strftime('%I:%M %p')}")
        )

