from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List

@dataclass
class Pet:
    petId: str
    name: str
    breed: str
    age: int
    owner: 'User' = None
    tasks: List['Task'] = field(default_factory=list)
    
    def getDetails(self) -> str:
        """Return a formatted string with the pet's name, breed, and age."""
        return f"{self.name} ({self.breed}), Age: {self.age}"
    
    def getScheduledWalks(self) -> List['Walk']:
        """Return a list of active (uncompleted) walks scheduled for this pet."""
        return [task.walk for task in self.tasks if task.walk and not task.isCompleted]


@dataclass
class Walk:
    walkId: str
    pet: Pet
    scheduledTime: datetime
    duration: int
    status: str = "scheduled"
    
    def scheduleWalk(self, time: datetime, duration: int) -> None:
        """Update the walk's scheduled time, duration, and mark as scheduled."""
        self.scheduledTime = time
        self.duration = duration
        self.status = "scheduled"
    
    def cancelWalk(self) -> None:
        """Mark the walk as cancelled."""
        self.status = "cancelled"
    
    def completeWalk(self) -> None:
        """Mark the walk as completed."""
        self.status = "completed"


@dataclass
class Task:
    taskId: str
    description: str
    dueDate: datetime
    priority: str
    isCompleted: bool = False
    walk: Walk = None
    user: 'User' = None
    pet: Pet = None
    recurrence: str = None  # "daily", "weekly", or None for one-time
    
    def markComplete(self) -> None:
        """Mark the task as complete and update associated walk status."""
        self.isCompleted = True
        if self.walk:
            self.walk.completeWalk()
    
    def getPriority(self) -> str:
        """Return the task's priority level."""
        return self.priority
    
    def isForToday(self) -> bool:
        """Check if the task is due today."""
        today = datetime.now().date()
        return self.dueDate.date() == today
    
    def getNextOccurrence(self) -> datetime:
        """Calculate the next occurrence date based on recurrence pattern."""
        if self.recurrence == "daily":
            return self.dueDate + timedelta(days=1)
        elif self.recurrence == "weekly":
            return self.dueDate + timedelta(weeks=1)
        else:
            return None


@dataclass
class User:
    userId: str
    name: str
    email: str
    pets: List[Pet] = field(default_factory=list)
    tasks: List[Task] = field(default_factory=list)
    walks: List[Walk] = field(default_factory=list)
    
    def addPet(self, pet: Pet) -> None:
        """Add a pet to the user's pet list and set the pet's owner."""
        pet.owner = self
        self.pets.append(pet)
    
    def getPets(self) -> List[Pet]:
        """Return the user's list of pets."""
        return self.pets
    
    def getTodaysTasks(self) -> List[Task]:
        """Return all uncompleted tasks due today for this user."""
        return [task for task in self.tasks if task.isForToday() and not task.isCompleted]


@dataclass
class Scheduler:
    """The 'Brain' that retrieves, organizes, and manages tasks across pets."""
    user: User
    
    def getAllTasks(self) -> List[Task]:
        """Return all tasks for the user."""
        return self.user.tasks
    
    def getTasksByPet(self, pet: Pet) -> List[Task]:
        """Return tasks filtered by a specific pet."""
        return [task for task in self.user.tasks if task.pet == pet]
    
    def getTasksByPriority(self, priority: str) -> List[Task]:
        """Return tasks filtered by priority level."""
        return [task for task in self.user.tasks if task.priority == priority]
    
    def scheduleWalk(self, pet: Pet, time: datetime, duration: int) -> Walk:
        """Create and schedule a walk for a pet, returning the Walk object."""
        
        # Check for conflicts before scheduling
        has_conflict, message = self.hasConflict(pet, time, duration)
        if has_conflict:
            print(message)
            print("⚠️  Walk not scheduled due to conflict.")
            return None
        
        walk = Walk(
            walkId=f"walk_{len(self.user.walks) + 1}",
            pet=pet,
            scheduledTime=time,
            duration=duration
        )
        task = Task(
            taskId=f"task_{len(self.user.tasks) + 1}",
            description=f"Walk {pet.name}",
            dueDate=time,
            priority="high",
            walk=walk,
            user=self.user,
            pet=pet
        )
        self.user.walks.append(walk)
        self.user.tasks.append(task)
        pet.tasks.append(task)
        
        print(f"✅ Walk scheduled for {pet.name} at {time.strftime('%I:%M %p')} ({duration} min)")
        return walk
    
    def completeTask(self, task: Task) -> Task:
        """
        Mark a task as complete and automatically create the next occurrence if recurring.
        
        This method implements the "recurring task expansion" pattern. When a recurring
        task (e.g., daily breakfast) is marked complete, a new Task instance is
        automatically created for the next occurrence using timedelta arithmetic.
        
        For example:
        - Daily task completed on Feb 15 → new task created for Feb 16
        - Weekly task completed on Feb 15 → new task created for Feb 22
        
        Args:
            task (Task): The task to mark as complete and potentially expand.
        
        Returns:
            Task: The newly created next occurrence (if recurring), or None (if one-time).
        
        Example:
            >>> daily_feed = Task(..., recurrence="daily", dueDate=datetime(2026,2,15,8,0))
            >>> next_feed = scheduler.completeTask(daily_feed)
            >>> if next_feed:
            ...     print(f"Next feeding scheduled for {next_feed.dueDate.strftime('%Y-%m-%d')}")
            ...     # Output: Next feeding scheduled for 2026-02-16
        
        Algorithm:
            1. Mark the current task isCompleted = True
            2. If task.recurrence exists, calculate next_due_date using getNextOccurrence()
            3. Clone the task with new taskId and next_due_date
            4. Add cloned task to both user.tasks and pet.tasks lists
            5. Return the new task (or None if one-time)
        """
        task.markComplete()
        
        # If task is recurring, create the next instance
        if task.recurrence:
            next_due_date = task.getNextOccurrence()
            if next_due_date:
                new_task = Task(
                    taskId=f"task_{len(self.user.tasks) + 1}",
                    description=task.description,
                    dueDate=next_due_date,
                    priority=task.priority,
                    isCompleted=False,
                    walk=None,  # Don't duplicate walk data
                    user=task.user,
                    pet=task.pet,
                    recurrence=task.recurrence
                )
                self.user.tasks.append(new_task)
                if task.pet:
                    task.pet.tasks.append(new_task)
                return new_task
        
        return None
    
    def createRecurringTask(self, pet: Pet, description: str, 
                          start_time: datetime, priority: str, 
                          recurrence: str) -> Task:
        """
        Create a new recurring task with automatic expansion support.
        
        Factory method that creates a new Task with recurrence metadata. Once created,
        when the task is marked complete via completeTask(), the system automatically
        generates the next occurrence in the sequence.
        
        Args:
            pet (Pet): The pet associated with this task.
            description (str): Human-readable task description (e.g., "Feed Buddy").
            start_time (datetime): The initial due date/time for the task.
            priority (str): Priority level: "high", "medium", or "low".
            recurrence (str): Recurrence pattern: "daily", "weekly", or None for one-time.
        
        Returns:
            Task: The newly created task with recurrence metadata set.
        
        Example:
            >>> today = datetime.now()
            >>> morning = today.replace(hour=8, minute=0)
            >>> daily_walk = scheduler.createRecurringTask(
            ...     pet=dog,
            ...     description="Morning walk",
            ...     start_time=morning,
            ...     priority="high",
            ...     recurrence="daily"
            ... )
            >>> print(f"Created: {daily_walk.description} (repeats {daily_walk.recurrence})")
        
        Note:
            The first instance is created with dueDate = start_time.
            Subsequent instances are generated when completeTask() is called.
        """
        task = Task(
            taskId=f"task_{len(self.user.tasks) + 1}",
            description=description,
            dueDate=start_time,
            priority=priority,
            isCompleted=False,
            user=self.user,
            pet=pet,
            recurrence=recurrence  # "daily", "weekly", or None
        )
        self.user.tasks.append(task)
        pet.tasks.append(task)
        return task
    
    def sortTasksByTime(self, tasks: List[Task]) -> List[Task]:
        """
        Sort tasks chronologically by their due date/time.
        
        Uses Python's sorted() with a lambda key function to order tasks
        in ascending time order. Useful for displaying tasks in the order
        they should be completed throughout the day.
        
        Args:
            tasks (List[Task]): A list of Task objects to sort.
        
        Returns:
            List[Task]: A new list of tasks sorted by dueDate in ascending order.
        
        Example:
            >>> sorted_tasks = scheduler.sortTasksByTime(pending_tasks)
            >>> # Tasks now appear earliest-first in the day
        """
        return sorted(tasks, key=lambda task: task.dueDate)
    
    def sortTasksByPriority(self, tasks: List[Task]) -> List[Task]:
        """
        Sort tasks by priority level, then chronologically by time.
        
        Implements multi-key sorting: high priority (0) → medium (1) → low (2),
        with tasks of equal priority sorted by dueDate. This ensures owners see
        the most urgent tasks first, while maintaining chronological order within
        each priority tier.
        
        Args:
            tasks (List[Task]): A list of Task objects to sort.
        
        Returns:
            List[Task]: A new list sorted by (priority_level, dueDate) tuples.
        
        Example:
            >>> urgent_first = scheduler.sortTasksByPriority(all_tasks)
            >>> # Red 🔴 tasks appear first, then yellow 🟡, then green 🟢
        """
        priority_order = {"high": 0, "medium": 1, "low": 2}
        return sorted(tasks, 
                      key=lambda task: (priority_order.get(task.priority, 3), task.dueDate))
    
    def getOrganizedTodaysTasks(self) -> dict:
        """
        Retrieve today's tasks organized by pet name and sorted by priority + time.
        
        This is the primary display method for daily schedules. It groups all
        pending tasks for today by pet, then sorts each pet's tasks first by
        priority (high → medium → low), then by time. This produces a nested
        dictionary structure ideal for multi-pet households.
        
        Args:
            None (uses self.user's tasks)
        
        Returns:
            dict: A dictionary mapping pet names (str) to lists of sorted Task objects.
                  Structure: {"Buddy": [Task, Task, ...], "Whiskers": [Task, ...]}
        
        Example:
            >>> organized = scheduler.getOrganizedTodaysTasks()
            >>> for pet_name, tasks in organized.items():
            ...     print(f"🐾 {pet_name}")
            ...     for task in tasks:
            ...         print(f"  {task.dueDate.strftime('%H:%M')} - {task.description}")
        """
        today_tasks = self.user.getTodaysTasks()
        organized = {}
        for task in today_tasks:
            pet_name = task.pet.name if task.pet else "General"
            if pet_name not in organized:
                organized[pet_name] = []
            organized[pet_name].append(task)
        
        # Sort each pet's tasks by priority, then time
        for pet_name in organized:
            organized[pet_name] = self.sortTasksByPriority(organized[pet_name])
        
        return organized
    
    def getTasksByStatus(self, completed: bool) -> List[Task]:
        """
        Return tasks filtered by completion status.
        
        A utility method for separating pending from completed tasks. Uses a simple
        list comprehension to filter by the isCompleted boolean flag.
        
        Args:
            completed (bool): True to return completed tasks, False for pending.
        
        Returns:
            List[Task]: All tasks matching the requested completion status.
        
        Example:
            >>> pending = scheduler.getTasksByStatus(completed=False)
            >>> done = scheduler.getTasksByStatus(completed=True)
        """
        return [task for task in self.user.tasks if task.isCompleted == completed]
    
    def getTasksByPetName(self, pet_name: str) -> List[Task]:
        """
        Return tasks filtered by pet name (case-insensitive).
        
        Enables quick lookup of all tasks for a specific pet by name. The search
        is case-insensitive to improve usability.
        
        Args:
            pet_name (str): The name of the pet to filter by.
        
        Returns:
            List[Task]: All tasks associated with the specified pet.
        
        Example:
            >>> buddy_tasks = scheduler.getTasksByPetName("Buddy")
            >>> # Returns all tasks for pets named "Buddy" (or "buddy", "BUDDY")
        """
        return [task for task in self.user.tasks if task.pet and task.pet.name.lower() == pet_name.lower()]
    
    def getPendingTasks(self) -> List[Task]:
        """
        Return all uncompleted tasks for the user.
        
        Convenience method equivalent to getTasksByStatus(completed=False).
        Useful for dashboard summaries and work-in-progress tracking.
        
        Returns:
            List[Task]: All tasks where isCompleted is False.
        
        Example:
            >>> todo = scheduler.getPendingTasks()
            >>> print(f"You have {len(todo)} tasks remaining today")
        """
        return [task for task in self.user.tasks if not task.isCompleted]
    
    def rescheduleMissedTasks(self) -> None:
        """Reschedule tasks that were due in the past and are not completed."""
        now = datetime.now()
        for task in self.user.tasks:
            if task.dueDate < now and not task.isCompleted:
                next_occurrence = task.getNextOccurrence()
                if next_occurrence:
                    task.dueDate = next_occurrence
                    task.markComplete()  # Optionally mark as complete if it's a past task
                    # Schedule a new task occurrence
                    new_task = Task(
                        taskId=f"task_{len(self.user.tasks) + 1}",
                        description=task.description,
                        dueDate=next_occurrence,
                        priority=task.priority,
                        recurrence=task.recurrence,
                        user=self.user,
                        pet=task.pet
                    )
                    self.user.tasks.append(new_task)
                    if task.walk:
                        # Optionally reschedule the associated walk
                        task.walk.scheduledTime = next_occurrence
                        task.walk.status = "scheduled"
    
    def hasConflict(self, pet: Pet, scheduled_time: datetime, duration: int = 30) -> tuple:
        """
        Check if a new task/walk conflicts with existing tasks for the same pet.
        
        Implements time-range overlap detection using the mathematical principle:
        Two ranges overlap if: range1_start < range2_end AND range1_end > range2_start
        
        This method scans all uncompleted walk tasks for a pet and checks whether
        the new scheduled time overlaps with any existing walks. For example, a
        30-minute walk at 8:00 AM (ends 8:30) will conflict with a walk at 8:15 AM.
        
        Args:
            pet (Pet): The pet for which to check conflicts.
            scheduled_time (datetime): The proposed start time for the new walk.
            duration (int): The duration of the new walk in minutes. Default: 30.
        
        Returns:
            tuple: (has_conflict: bool, conflict_message: str)
                   - has_conflict: True if overlap detected, False if safe to schedule
                   - conflict_message: User-friendly message with conflict details or confirmation
        
        Example:
            >>> has_conflict, msg = scheduler.hasConflict(dog, morning_time, 30)
            >>> if has_conflict:
            ...     print(msg)  # "⚠️  CONFLICT: Buddy already has 'Walk Buddy' at 08:15 AM..."
            >>> else:
            ...     scheduler.scheduleWalk(dog, morning_time, 30)
        
        Note:
            This is a "lightweight" approach that returns warnings instead of
            throwing exceptions, allowing graceful error handling in the UI layer.
        """
        new_end_time = scheduled_time + timedelta(minutes=duration)
        conflicts = []
        
        # Get all uncompleted tasks for this pet
        pet_tasks = [task for task in pet.tasks if not task.isCompleted]
        
        for task in pet_tasks:
            if task.walk:
                # This is a walk task, check for time overlap
                task_end_time = task.dueDate + timedelta(minutes=task.walk.duration)
                
                # Check if new task overlaps with existing task
                # Overlap occurs if: new_start < existing_end AND new_end > existing_start
                if scheduled_time < task_end_time and new_end_time > task.dueDate:
                    existing_time = task.dueDate.strftime("%I:%M %p")
                    new_time = scheduled_time.strftime("%I:%M %p")
                    conflicts.append(
                        f"⚠️  CONFLICT: {pet.name} already has '{task.description}' "
                        f"at {existing_time} (duration: {task.walk.duration} min)"
                    )
        
        if conflicts:
            return (True, "\n".join(conflicts))
        else:
            return (False, f"✅ No conflicts found for {pet.name} at {scheduled_time.strftime('%I:%M %p')}")
    
    def checkAllConflicts(self) -> list:
        """
        Scan all tasks and return a list of all conflicts across all pets.
        
        This is a comprehensive validation method that checks the entire schedule
        for any overlapping walks across all pets in the user's household. Unlike
        hasConflict() which checks a single proposed walk, checkAllConflicts()
        examines all existing walks pairwise to identify any inconsistencies.
        
        Useful for validation, reporting, and detecting scheduling errors that may
        have accumulated from user manual edits or system bugs.
        
        Returns:
            list: A list of conflict description strings (empty if no conflicts).
                  Each string contains the pet name, task names, and times involved.
        
        Example:
            >>> conflicts = scheduler.checkAllConflicts()
            >>> if conflicts:
            ...     for conflict in conflicts:
            ...         print(conflict)
            ... else:
            ...     print("✅ Schedule is conflict-free!")
        
        Algorithmic Complexity:
            - Time: O(p * n^2) where p = number of pets, n = average tasks per pet
            - Space: O(c) where c = number of conflicts found
        """
        all_conflicts = []
        
        for pet in self.user.pets:
            pet_tasks = [task for task in pet.tasks if not task.isCompleted and task.walk]
            
            # Compare each task with every other task for the same pet
            for i, task1 in enumerate(pet_tasks):
                for task2 in pet_tasks[i + 1:]:
                    task1_end = task1.dueDate + timedelta(minutes=task1.walk.duration)
                    task2_end = task2.dueDate + timedelta(minutes=task2.walk.duration)
                    
                    # Check for overlap
                    if task1.dueDate < task2_end and task1_end > task2.dueDate:
                        conflict_msg = (
                            f"🔴 CONFLICT DETECTED\n"
                            f"   Pet: {pet.name}\n"
                            f"   Task 1: {task1.description} at {task1.dueDate.strftime('%I:%M %p')}\n"
                            f"   Task 2: {task2.description} at {task2.dueDate.strftime('%I:%M %p')}"
                        )
                        all_conflicts.append(conflict_msg)
        
        return all_conflicts