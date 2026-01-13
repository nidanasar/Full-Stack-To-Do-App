# Feature: Task CRUD Operations

## Overview
Core functionality for creating, reading, updating, and deleting tasks.

## User Stories

### Create Task
- As a user, I can create a new task with a title
- As a user, I can optionally add a description to a task

### Read Tasks
- As a user, I can view all my tasks
- As a user, I can view task details
- As a user, I can filter tasks by status (completed/pending)

### Update Task
- As a user, I can edit task title and description
- As a user, I can mark a task as complete/incomplete

### Delete Task
- As a user, I can delete a task
- As a user, I receive confirmation before deletion

## Acceptance Criteria
- [ ] Tasks persist across page refreshes
- [ ] Tasks are associated with authenticated user
- [ ] Empty task titles are not allowed
- [ ] Task status toggle is immediate (optimistic UI)
