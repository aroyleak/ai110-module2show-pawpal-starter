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
    
    def getDetails(self) -> str:
        pass
    
    def getScheduledWalks(self) -> List['Walk']:
        pass


@dataclass
class Walk:
    walkId: str
    pet: Pet
    scheduledTime: datetime
    duration: int
    status: str = "scheduled"
    
    def scheduleWalk(self, time: datetime, duration: int) -> None:
        pass
    
    def cancelWalk(self) -> None:
        pass
    
    def completeWalk(self) -> None:
        pass


@dataclass
class Task:
    taskId: str
    description: str
    dueDate: datetime
    priority: str
    isCompleted: bool = False
    walk: Walk = None
    
    def markComplete(self) -> None:
        pass
    
    def getPriority(self) -> str:
        pass
    
    def isForToday(self) -> bool:
        pass


@dataclass
class User:
    userId: str
    name: str
    email: str
    pets: List[Pet] = field(default_factory=list)
    
    def addPet(self, pet: Pet) -> None:
        pass
    
    def getPets(self) -> List[Pet]:
        pass
    
    def getTodaysTasks(self) -> List[Task]:
        pass