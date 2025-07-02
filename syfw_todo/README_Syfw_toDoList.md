# Syfw toDoList AI assistant

Syfw toDoList AI assistant project


## Syfw Configuration & Deployment
1. Go to synthflow.ai
Start by creating an account if you do not have an account and logging in.

2. Go to Synthflow menu in the left panel and create agent.

<img width="1247" alt="image" src="https://github.com/user-attachments/assets/5d3257dd-457a-4a63-bdc4-276715e359b5" />

3. Go to Actions menu and create Custom Actions.
+ toDoList
    + createTodo
      ![createTodo_action](https://github.com/user-attachments/assets/2fac6d76-7cbc-4dd4-936d-a06f302f2874)
    + getTodos
    + completeTodo
    + deleteTodo
+ reMinder
    * addReminder
    * getReminder
    * deleteReminder
+ calendar
    - addCalendarEntry
    - getCalendarEntries
    - deleteCalendarEntry

4. Configure Agent
  + General
    * AI Model: GPT 4o or something you want
    * timezone: US/Pacific
  + Voice
    * Language: English or language you prefer
    * Voice: Jessica or something you prefer
  + Call Configuration
    * Enable Recording: Purple enabled
    * Enable Transcripts: Purple enabled
    
5. Configure Prompt  
  + Greeting message
    * simple greeting message
  + Prompt
    * Agent Information: 
    * Personality: 
    * Role: 
    * Goal:
    * Conversation Style:
    * Script Instructions: 

6. Configure Actions  
  + Select Before or During or After the call
    * add actions to the selected the call

7. Deployment  
  + Select Phone number
    * simple greeting message


## Test AI Voice scheuduler
1. Make a call and say "to do list with time and date" to AI assistant
2. Make a call and ask what "to do lists" exist currently and ask to remind the tasks
3. Make a call and say that some tasks were completed
4. Make a call and say that some tasks were deleted
5. Check whether all test cases have been updated to Database tables

   

