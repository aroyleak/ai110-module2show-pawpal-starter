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

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
