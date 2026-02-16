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

