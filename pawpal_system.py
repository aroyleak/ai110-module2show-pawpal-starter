from dataclasses import dataclass, field
from datetime import datetime
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
        return walk
    
    def completeTask(self, task: Task) -> None:
        """Mark a task as complete."""
        task.markComplete()
    
    def getOrganizedTodaysTasks(self) -> dict:
        """Return today's tasks organized by pet name."""
        today_tasks = self.user.getTodaysTasks()
        organized = {}
        for task in today_tasks:
            pet_name = task.pet.name if task.pet else "General"
            if pet_name not in organized:
                organized[pet_name] = []
            organized[pet_name].append(task)
        return organized