# BLND TodoList: Technical Specification & Architecture

### 1. High-Level Overview

The `blnd_todo` is a modular and self-contained component, implemented as a Flask Blueprint, that provides a complete Voice AI solution for managing tasks, reminders, and calendar events through natural language processing. It is designed to be seamlessly integrated into a larger Flask application, as demonstrated by its registration within the `create_app` factory in `app.py`.

The architecture emphasizes a clear separation of concerns, with distinct modules for routes and logic (`routes.py`), database models (`models.py`), and integration with external services (Google Calendar API). This modularity makes the project scalable, maintainable, and easy to test.

### 2. Core Architecture & Design Patterns

#### a. Flask Blueprint (`blnd_todo_bp`)

The entire functionality of the BLND Todo system is encapsulated within a single Flask Blueprint named `blnd_todo_bp`.

* **Definition**: The blueprint is defined in `blnd_todo/routes.py`. This file serves as the central hub for the BLND Todo's API endpoints and view functions.
  ```python
  blnd_todo_bp = Blueprint(
      'blnd_todo',
      __name__,
      url_prefix='/blnd_todo',
      template_folder='templates',
      static_folder='static'
  )
  ```
* **Modularity**: It has its own dedicated `static_folder` and `template_folder`, ensuring its frontend assets are neatly organized and decoupled from the main application or other blueprints.
* **Integration**: In `app.py`, the blueprint is registered with the main Flask application using a `url_prefix='/blnd_todo'`. This means all routes defined within the blueprint (e.g., `/create_todo`, `/get_todos`) are accessible under the prefixed path (e.g., `https://hjlees.com/blnd_todo/create_todo`).

#### b. Voice AI Integration Pattern

The project implements a sophisticated Voice AI integration pattern that bridges natural language processing with structured database operations:

* **Tool Call Validation**: Each endpoint uses the `get_validated_tool_call()` function from `shared.helpers` to validate incoming BLND tool calls and extract function arguments.
* **Stateless API Design**: All endpoints are stateless and designed to handle requests from the BLND Voice AI platform, returning standardized JSON responses.
* **Error Handling**: Comprehensive error handling ensures graceful degradation when external services (Google Calendar) are unavailable.

### 3. Database and Data Layer

#### a. ORM and Models

* **Technology**: The project uses **Flask-SQLAlchemy** as its Object-Relational Mapper (ORM) to interact with the PostgreSQL database.
* **Model Definitions**: The database schema is defined in `blnd_todo/models.py` using SQLAlchemy Column definitions. The core models are:
  
  * `BlndTodo`: Represents a todo item with `title`, `description`, `completed` status, and optional `google_calendar_event_id` for synchronization.
  * `BlndReminder`: Represents a reminder with `reminder_text`, `importance` level, and optional `google_calendar_event_id`.
  * `BlndCalendarEvent`: Represents a calendar event with `title`, `description`, `event_from`, `event_to` timestamps, and optional `google_calendar_event_id`.

* **Relationships**: While the models are independent, they share a common pattern of Google Calendar integration through the `google_calendar_event_id` field, enabling bidirectional synchronization.

#### b. Database Migrations

The project is integrated with **Flask-Migrate**, which uses Alembic to handle database schema migrations. This allows for version-controlled, programmatic updates to the database structure as the application's models evolve.

### 4. API Endpoints and Voice AI Integration

#### a. Todo Management Endpoints

* **`/create_todo` (POST)**: Creates a new todo item and optionally syncs with Google Calendar
* **`/get_todos` (POST)**: Retrieves all todo items from the database
* **`/complete_todo` (POST)**: Marks a todo as completed and updates the corresponding Google Calendar event
* **`/delete_todo` (POST)**: Deletes a todo item and removes the corresponding Google Calendar event

#### b. Reminder Management Endpoints

* **`/add_reminder` (POST)**: Creates a new reminder and optionally syncs with Google Calendar
* **`/get_reminders` (POST)**: Retrieves all reminders from the database
* **`/delete_reminder` (POST)**: Deletes a reminder and removes the corresponding Google Calendar event

#### c. Calendar Event Management Endpoints

* **`/add_calendar_entry` (POST)**: Creates a new calendar event and syncs with Google Calendar
* **`/get_calendar_entries` (POST)**: Retrieves all calendar events from the database
* **`/delete_calendar_entry` (POST)**: Deletes a calendar event and removes it from Google Calendar

### 5. External Service Integration

#### a. Google Calendar API Integration

The project seamlessly integrates with Google Calendar through the `shared.google_calendar` module:

* **Event Creation**: When a todo, reminder, or calendar event is created, it's automatically synced to Google Calendar
* **Event Updates**: When a todo is completed, the corresponding Google Calendar event is updated to reflect the completion status
* **Event Deletion**: When items are deleted, the corresponding Google Calendar events are also removed
* **Error Handling**: Graceful error handling ensures the application continues to function even if Google Calendar is unavailable

#### b. BLND Voice AI Platform Integration

The project is designed to work with the BLND Voice AI platform:

* **Tool Call Validation**: Each endpoint validates incoming tool calls from BLND to ensure data integrity
* **Standardized Responses**: All endpoints return responses in the format expected by BLND
* **Natural Language Processing**: The system accepts natural language commands through BLND and converts them to structured database operations

### 6. Data Flow Example: Creating a Todo via Voice

1. **Voice Input**: User calls the BLND assistant and says "Create a todo to buy groceries tomorrow"
2. **BLND Processing**: BLND processes the natural language and calls the `createTodo` tool with structured parameters
3. **API Request**: BLND sends a POST request to `/blnd_todo/create_todo` with the tool call data
4. **Validation**: The endpoint validates the tool call using `get_validated_tool_call('createTodo')`
5. **Database Operation**: A new `BlndTodo` record is created in the PostgreSQL database
6. **Google Calendar Sync**: The system attempts to create a corresponding Google Calendar event
7. **Response**: A success response is returned to BLND, which confirms the action to the user via voice

### 7. Security and Error Handling

#### a. Input Validation

* **Tool Call Validation**: All incoming requests are validated to ensure they contain proper tool call data
* **Parameter Validation**: Required parameters are checked before processing
* **Database Constraints**: SQLAlchemy models enforce data integrity at the database level

#### b. Error Handling

* **Graceful Degradation**: If Google Calendar is unavailable, the system continues to function with local database operations
* **Comprehensive Logging**: All errors are logged for debugging and monitoring
* **User-Friendly Responses**: Errors are handled gracefully and appropriate responses are returned to BLND

### 8. Deployment and Configuration

#### a. BLND Platform Configuration

The project requires configuration on the BLND platform:

1. **Tool Creation**: Create tools for `createTodo`, `getTodos`, `completeTodo`, `deleteTodo`, `addReminder`, `getReminders`, `deleteReminder`, `addCalendarEntry`, `getCalendarEntries`, `deleteCalendarEntry`
2. **Assistant Configuration**: Configure an assistant with the appropriate model, voice, and transcriber settings
3. **Tool Assignment**: Assign the created tools to the assistant

#### b. Environment Configuration

* **Database**: PostgreSQL database with the required tables
* **Google Calendar API**: Properly configured Google Calendar API credentials
* **Flask Application**: Integration with the main Flask application through blueprint registration

### 9. Frontend Integration

The BLND Todo system includes a web interface for manual management:

* **Main Interface**: Accessible at `/blnd_todo/` route, providing a user-friendly interface for managing todos, reminders, and calendar events
* **Template System**: Uses Flask templates for rendering the web interface
* **Static Assets**: Dedicated static folder for CSS, JavaScript, and other frontend assets

This architecture creates a robust, maintainable, and feature-rich Voice AI Todo system that seamlessly integrates natural language processing with structured database operations and external service synchronization, while also providing a web interface for manual management.
