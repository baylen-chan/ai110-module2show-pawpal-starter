# PawPal+ Project Reflection

## 1. System Design

- 1. The user should be able to add their pets into the system.
- 2. The user should be able to schedule certain events. This includes feeding, walks, etc.
- 3. The user should also have the option to view their tasks after inputting the information in.

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?
  My UML design has four classes. The CareTask class holds details such as the name, type, duration, priority, preferred time, recurrance. It compares tasks with one another by priority and whether it fits in the time. The Pets class holds the pet's info such as name, species, bred, age. The Pet class also holds the list of its CareTasks. THe Scheduler class does the planning and sorts by priority. It filters them to fit a time and generates the plan. The DailyPlan class is the output. It will display the plan.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.
  Yes, there were changes. I first stored times and priority as plain text ("08:00", "high"), but the scheduler couldn't do math on a string or sort by it. So I switched times to numbers (minutes since midnight) and made priority an Enum, and added a small ScheduledEntry class to track each task's start/end — which made detecting overlaps easier.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?
When two tasks overlap, my scheduler only warns the owner instead of moving one automatically. I chose to return a warning message rather than reschedule or crash, so the rest of the plan still prints. This is reasonable because the owner knows their pet's routine best, and a warning lets them decide what to move instead of the program silently changing a task they cared about.

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
