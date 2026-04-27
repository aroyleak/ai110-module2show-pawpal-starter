# PawPal+ Project Reflection

## 1. System Design


**a1 Three Actions
Three actions a user should be able to do and perform is to be able to do is add their pet, schedule a walk and see today's viewing tasks. 

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

The classes I chose to make were "Walk", "Pet", "User" and "Task" classes.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

New Relationships: I added bidirectional connections to strengthen the data model. Task now references both user and pet, while User now holds collections of tasks and walks. This creates clear ownership chains throughout the system.

Why It Matters: These changes eliminate bottlenecks by organizing data hierarchically. Instead of searching globally for today's tasks, getTodaysTasks() now queries the user's own task list. The app is now more scalable, efficient, and intuitive.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The scheduler considers three main constraints: time (when a task is due), priority level (high, medium, or low), and walk overlap (whether two walks for the same pet conflict in time). I decided priority mattered most because a high-priority feeding scheduled later in the day should still appear before a low-priority task scheduled earlier — so priority is the first sort key, with time as the tiebreaker. Conflict detection was also critical because scheduling two overlapping walks for the same pet is a real-world problem that would cause the owner to fail both tasks.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

Tradeoff: Overlap Detection vs. Exact Time Matching

Two paths diverged in scheduling logic:
One path checked exact times with mathematical precision,
The other honored duration, respecting the temporal reality of care.
We chose the longer road—overlap detection—
Because real walks take time, and truth matters more than simplicity.
A small calculation trades for correctness,
And owners sleep soundly knowing conflicts are truly caught.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used AI tools primarily for brainstorming the class structure, writing docstrings, and debugging logic in the scheduler. The most helpful prompts were specific ones — for example, asking "how should overlap detection work if two walks share the same start time?" produced a clear mathematical explanation I could directly translate into code. I also used AI to help write the test cases once the logic was complete, describing the behavior I wanted to verify and having it generate the test structure.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

When AI suggested storing walk references directly inside the `Pet` class as a `scheduledWalks` list, I pushed back because it created redundancy — walks were already tracked through tasks and on the `User`. Instead I kept a computed method `getScheduledWalks()` on `Pet` that derives the list from existing task data. I verified the choice by tracing through what data would need to be updated if a walk was cancelled — with a separate list, I'd have to update two places; with the computed method, cancellation was handled in one spot automatically.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I tested four core behaviors: sorting correctness (does priority + time ordering work?), recurring task expansion (does completing a daily task create tomorrow's task?), conflict detection (does the scheduler block overlapping walks?), and filtering logic (can you pull tasks by pet name or completion status?). These were the most important behaviors to test because they form the backbone of the app — if any of them break silently, the entire schedule becomes unreliable without the user knowing.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I'm confident the core logic is correct — all 24 tests pass and cover both normal cases and edge cases like empty lists, single items, and boundary times. If I had more time, I'd test what happens when a pet is deleted mid-schedule (tasks still reference the pet object), and whether recurring tasks correctly stop if a user manually removes them from the list before the next completion cycle.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I'm most satisfied with the conflict detection logic. It's a clean, mathematically sound implementation — the overlap formula (`new_start < existing_end AND new_end > existing_start`) handles all edge cases including back-to-back walks, partial overlaps, and completed walks that shouldn't block new scheduling. Seeing all 10 conflict tests pass gave me real confidence that the logic held up under pressure.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I would redesign how recurring tasks are stored. Right now, completing a task appends a new Task object to the list every time. Over weeks of use, the task list would grow indefinitely with completed entries. A better design would store a recurrence rule separately and generate upcoming tasks on demand, rather than materializing every future task as a new object.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

The biggest lesson was that AI is most useful when you understand the problem well enough to verify its output. When I asked vague questions, I got generic answers. When I asked specific questions — like "what happens at the boundary between two back-to-back walks?" — the AI gave precise, testable answers. The skill isn't just prompting; it's knowing enough to evaluate what comes back.
