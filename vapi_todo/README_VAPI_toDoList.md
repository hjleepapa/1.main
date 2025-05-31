# VAPI toDoList AI assistant into Portfolio

VAPI toDoList AI assistant project added to Portfolio website

## Table of Contents

-[Installation](#installation)
-[Usage](#usage)
-[Configuration](#Configuration)
-[License](#license)

## Installation

## VAPI Configuration & Deployment
1. Go to Vapi.AI
Start by creating an account if you do not have an account and logging in.

2. Access the Dashboard and create tool.
Once logged in, go to your dashboard and click on “Create Tool” in Tools/Build of the left panel.
<img width="1247" alt="image" src="https://github.com/user-attachments/assets/5d3257dd-457a-4a63-bdc4-276715e359b5" />

3. Create Tool functions with each required Parameters, Server Settings
+ toDoList
    + createTodo
      ![createTodo_tool](https://github.com/user-attachments/assets/2fac6d76-7cbc-4dd4-936d-a06f302f2874)
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

4. Create Assistant in Assistants/BUILD
  + Model
    * Provider: OpenAI or something you prefer
    * Model: GPT 4o Cluster or something you want
    * First Message: modify first message
  + Voice
    * Provider: OpenAI or something you prefer
    * Model: GPT
  + Transcriber
    * Provider: Deepgram or something you prefer
    * Language: En or language you prefer
    * Tools: select the functions you created in step 3.
  + Tools
    * Tools: select the functions you created in step 3.

5. Once creating an assistant and tools, click "published"

## Create API functions to respond with requests (vapi1_flask.py)

![vapi1_flask](https://github.com/user-attachments/assets/66bb08d9-c7fd-4b65-98d8-2cc91c5851a8)

