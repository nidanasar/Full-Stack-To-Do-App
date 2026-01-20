"""Task CRUD routes with JWT authentication."""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import CurrentUser, DbSession
from exceptions import NotFoundException
from models import Task
from schemas import TaskCreate, TaskListResponse, TaskPatch, TaskResponse, TaskUpdate


async def get_task_with_ownership(
    db: AsyncSession, task_id: UUID, user_id: UUID
) -> Task:
    """Get a task by ID with ownership verification.

    Returns 404 for both non-existent tasks and tasks owned by other users
    to prevent task ID enumeration.

    Args:
        db: Database session.
        task_id: Task UUID to fetch.
        user_id: Current user's UUID from JWT.

    Returns:
        Task if found and owned by user.

    Raises:
        NotFoundException: If task not found or owned by different user.
    """
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    )
    task = result.scalar_one_or_none()

    if task is None:
        raise NotFoundException("Task not found")

    return task


class SortField(str, Enum):
    """Valid fields for sorting tasks."""

    created_at = "created_at"
    updated_at = "updated_at"
    title = "title"
    completed = "completed"


class SortOrder(str, Enum):
    """Sort order options."""

    asc = "asc"
    desc = "desc"

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"description": "Missing or invalid JWT"},
        422: {"description": "Validation error (empty/invalid title)"},
    },
)
async def create_task(
    data: TaskCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> TaskResponse:
    """Create a new task for the authenticated user.

    The user_id is extracted from the JWT token, never from the request body.

    Args:
        data: Task creation data (title, optional description).
        db: Database session.
        current_user: User ID from JWT token.

    Returns:
        TaskResponse with created task data.

    Raises:
        UnauthorizedException: If JWT is missing or invalid.
        ValidationException: If title is empty or exceeds limits.
    """
    task = Task(
        user_id=current_user,
        title=data.title,
        description=data.description,
    )

    db.add(task)
    await db.flush()
    await db.refresh(task)

    return TaskResponse.model_validate(task)


@router.get(
    "",
    response_model=TaskListResponse,
    responses={
        401: {"description": "Missing or invalid JWT"},
    },
)
async def list_tasks(
    db: DbSession,
    current_user: CurrentUser,
    completed: Optional[bool] = Query(default=None, description="Filter by completion status"),
    sort: SortField = Query(default=SortField.created_at, description="Field to sort by"),
    order: SortOrder = Query(default=SortOrder.desc, description="Sort order"),
) -> TaskListResponse:
    """List all tasks for the authenticated user.

    Tasks are filtered by user_id from JWT (user isolation enforced).
    Supports optional filtering by completion status and sorting.

    Args:
        db: Database session.
        current_user: User ID from JWT token.
        completed: Optional filter for completion status.
        sort: Field to sort by (default: created_at).
        order: Sort order (default: desc).

    Returns:
        TaskListResponse with list of user's tasks.

    Raises:
        UnauthorizedException: If JWT is missing or invalid.
    """
    # Base query with user isolation - only get current user's tasks
    query = select(Task).where(Task.user_id == current_user)

    # Apply optional completed filter
    if completed is not None:
        query = query.where(Task.completed == completed)

    # Apply sorting
    sort_column = getattr(Task, sort.value)
    if order == SortOrder.desc:
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    result = await db.execute(query)
    tasks = result.scalars().all()

    return TaskListResponse(
        tasks=[TaskResponse.model_validate(task) for task in tasks]
    )


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    responses={
        401: {"description": "Missing or invalid JWT"},
        404: {"description": "Task not found or not owned by user"},
    },
)
async def get_task(
    task_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> TaskResponse:
    """Get a single task by ID.

    Returns 404 for both non-existent tasks and tasks owned by other users
    to prevent enumeration attacks.

    Args:
        task_id: UUID of the task to retrieve.
        db: Database session.
        current_user: User ID from JWT token.

    Returns:
        TaskResponse with task data.

    Raises:
        UnauthorizedException: If JWT is missing or invalid.
        NotFoundException: If task not found or owned by different user.
    """
    task = await get_task_with_ownership(db, task_id, current_user)
    return TaskResponse.model_validate(task)


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    responses={
        401: {"description": "Missing or invalid JWT"},
        404: {"description": "Task not found or not owned by user"},
        422: {"description": "Validation error"},
    },
)
async def update_task(
    task_id: UUID,
    data: TaskUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> TaskResponse:
    """Full update of a task (all fields required).

    Replaces all task fields with provided values.
    Auto-updates the updated_at timestamp.

    Args:
        task_id: UUID of the task to update.
        data: Full task update data.
        db: Database session.
        current_user: User ID from JWT token.

    Returns:
        TaskResponse with updated task data.

    Raises:
        UnauthorizedException: If JWT is missing or invalid.
        NotFoundException: If task not found or owned by different user.
    """
    task = await get_task_with_ownership(db, task_id, current_user)

    # Update all fields
    task.title = data.title
    task.description = data.description
    task.completed = data.completed
    task.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)

    await db.flush()
    await db.refresh(task)

    return TaskResponse.model_validate(task)


@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
    responses={
        401: {"description": "Missing or invalid JWT"},
        404: {"description": "Task not found or not owned by user"},
        422: {"description": "Validation error"},
    },
)
async def patch_task(
    task_id: UUID,
    data: TaskPatch,
    db: DbSession,
    current_user: CurrentUser,
) -> TaskResponse:
    """Partial update of a task (only provided fields updated).

    Updates only the fields that are explicitly provided.
    Auto-updates the updated_at timestamp if any field changes.

    Args:
        task_id: UUID of the task to patch.
        data: Partial task update data.
        db: Database session.
        current_user: User ID from JWT token.

    Returns:
        TaskResponse with updated task data.

    Raises:
        UnauthorizedException: If JWT is missing or invalid.
        NotFoundException: If task not found or owned by different user.
    """
    task = await get_task_with_ownership(db, task_id, current_user)

    # Update only provided fields
    update_data = data.model_dump(exclude_unset=True)
    has_changes = False

    for field, value in update_data.items():
        if getattr(task, field) != value:
            setattr(task, field, value)
            has_changes = True

    # Auto-update timestamp if any field changed
    if has_changes:
        task.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)

    await db.flush()
    await db.refresh(task)

    return TaskResponse.model_validate(task)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {"description": "Missing or invalid JWT"},
        404: {"description": "Task not found or not owned by user"},
    },
)
async def delete_task(
    task_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> None:
    """Delete a task by ID.

    Returns 404 for both non-existent tasks and tasks owned by other users
    to prevent enumeration attacks.

    Args:
        task_id: UUID of the task to delete.
        db: Database session.
        current_user: User ID from JWT token.

    Returns:
        None (204 No Content on success).

    Raises:
        UnauthorizedException: If JWT is missing or invalid.
        NotFoundException: If task not found or owned by different user.
    """
    task = await get_task_with_ownership(db, task_id, current_user)
    await db.delete(task)
