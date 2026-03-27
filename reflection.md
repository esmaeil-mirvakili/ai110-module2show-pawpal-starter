# PawPal+ Project Reflection

## 1. System Design

### Core User Actions

- Enter and manage basic owner and pet information so the app can personalize the plan around the pet's needs and the owner's preferences.
- Create and manage pet care tasks such as walks, feeding, medication, grooming, and enrichment, including details like duration and priority.
- Generate and review a daily care plan that organizes those tasks into a realistic schedule and explains why certain tasks were selected or ordered the way they were.

**a. Initial design**

- Briefly describe your initial UML design.
  - My initial UML design focused on separating the system into a few clear objects with specific responsibilities. The goal was to keep the data model simple while still supporting the main user actions: managing pet and owner information, creating care tasks, and generating a daily plan.
- What classes did you include, and what responsibilities did you assign to each?
  - I included an `Owner` class to store the pet owner's information, available time, preferences, and notes. I used a `Pet` class to represent the pet's profile, including details like name, species, age, energy level, and health notes.
  - I created a `CareTask` class to represent individual pet care activities such as walks, feeding, medication, grooming, or enrichment. This class holds task details like duration, priority, due time, and whether the task is required.
  - I also included a `ScheduleEntry` class so a task could be placed into a daily schedule with a start time, end time, and a short reason for why it appears there.
  - To organize the final output, I used a `DailyPlan` class to store scheduled tasks, total planned time, explanations, and any tasks that could not fit into the day. Finally, I used a `Scheduler` class as the main decision-making component responsible for applying constraints like time and priority and generating the daily plan.

**b. Design changes**

- Did your design change during implementation?
  - Yes. One change was that I separated the idea of a task from the idea of a scheduled task instead of treating them as the same object.
- If yes, describe at least one change and why you made it.
  - I added a `ScheduleEntry` class to represent a task after it has been placed into the daily plan with a start time, end time, and explanation. I made this change because a `CareTask` only describes what needs to be done, while a scheduled entry describes when and why it will happen. Separating those responsibilities makes the design clearer and makes it easier to build, display, and adjust a daily schedule later.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
  - My scheduler considers the owner's available time, whether a task is required, the task's priority level, and the task's preferred due time. It also includes owner preferences in the explanation logic so the final plan can reflect why a task matched what the owner wanted.
- How did you decide which constraints mattered most?
  - I decided that available time and required tasks mattered most because a realistic daily plan has to fit within the time the owner actually has, and some tasks like feeding or medication are more important than optional activities. After that, I used priority and due time to decide the order of the remaining tasks.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
  - One tradeoff my scheduler makes is that it uses a simple greedy approach: it sorts tasks by required status, priority, and due time, then adds tasks until the available time runs out. It does not try every possible task combination to find the absolute best schedule.
- Why is that tradeoff reasonable for this scenario?
  - That tradeoff is reasonable because this project is meant to be understandable, fast, and easy to explain. A greedy scheduler is much simpler to build and debug, and it still gives a useful daily plan for a pet owner without adding unnecessary complexity.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
  - I used AI to brainstorm the initial system design, turn the UML ideas into class skeletons, suggest ways to connect the backend to the Streamlit UI, and help refine the scheduler with features like sorting, filtering, recurrence, and conflict warnings. I also used it while debugging and while organizing the reflection and README documentation.
- What kinds of prompts or questions were most helpful?
  - The most helpful prompts were specific and concrete, especially when I asked for one change at a time. Prompts such as creating a Mermaid class diagram, adding a certain method, writing targeted tests, or updating one section of the reflection were more useful than broad requests because they made the output easier to verify.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
  - One moment where I did not accept an AI suggestion as-is was when I asked for reflection answers and the response replaced the original prompt questions instead of keeping them in the template. That format did not match what I needed for the assignment.
- How did you evaluate or verify what the AI suggested?
  - I evaluated it by comparing the file output to the required reflection structure and then asked for a correction so each question stayed in place with its answer underneath. More generally, I verified code suggestions by running `py_compile`, running `pytest`, and checking terminal output from `main.py` to make sure the behavior matched the intended design.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
  - I tested task completion, adding a task to a pet, sorting tasks by time, creating the next occurrence for daily recurring tasks, and detecting scheduling conflicts for both the same pet and different pets.
- Why were these tests important?
  - These tests were important because they cover the most important scheduling behaviors in the app. They check that the task data changes correctly, that task lists update correctly, that sorting works as expected, that recurring tasks continue automatically, and that conflicts are detected without crashing the program.

**b. Confidence**

- How confident are you that your scheduler works correctly?
  - I am fairly confident that the scheduler works correctly for the core scenarios I implemented. The main features pass automated tests, and I also checked the output manually in the terminal and in the Streamlit UI.
- What edge cases would you test next if you had more time?
  - If I had more time, I would test tasks with no due time, tasks with invalid time input, tasks that are longer than the owner's total available time, repeated completion of recurring tasks, and more complex cross-pet scheduling cases where several overlaps happen at once.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
  - I am most satisfied with how the project grew from a simple starter app into a more complete system with classes, scheduling logic, a terminal demo, tests, and a Streamlit interface. The final design feels much more structured than the initial placeholder app.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
  - In another iteration, I would redesign the scheduler so it could manage multiple pets in one combined daily plan instead of handling one pet per scheduler instance. I would also improve the optimization logic so it could make smarter decisions than the current greedy approach.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
  - One important thing I learned is that good system design depends on separating responsibilities clearly and testing small pieces as they are built. I also learned that AI is most useful when I give precise instructions and then verify the output carefully instead of assuming the first answer is correct.
