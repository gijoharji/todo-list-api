#To-Do List API (FastAPI)

This is a RESTful To-Do List API built with **FastAPI** and **SQLAlchemy**, deployed on **Render**, using **PostgreSQL** for persistent data storage.

It includes key features such as:
- Task management (CRUD)
- Data collection via logging
- Data analysis via `/stats` endpoint
- Simulated messaging queue using `ThreadPoolExecutor`

---

##Features

###CRUD Operations
- `POST /tasks/` – Create a new task
- `GET /tasks/` – Retrieve all tasks
- `GET /tasks/{task_id}` – Retrieve a task by ID
- `PUT /tasks/{task_id}` – Update a task
- `PUT /tasks/{task_id}/complete` – Mark a task as completed
- `DELETE /tasks/{task_id}` – Delete a task

###Data Analysis Endpoint
- `GET /stats/`
  ```json
  {
    "total_tasks": 10,
    "completed_tasks": 6,
    "pending_tasks": 4
  }

