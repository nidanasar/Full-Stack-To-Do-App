"""Tests for task CRUD endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from models import Task, User


class TestCreateTask:
    """Tests for POST /api/v1/tasks."""

    async def test_create_task_success(
        self, client: AsyncClient, auth_headers: dict, test_user: User
    ):
        """Create task with valid data returns 201."""
        response = await client.post(
            "/api/v1/tasks",
            headers=auth_headers,
            json={"title": "New Task", "description": "Task description"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Task"
        assert data["description"] == "Task description"
        assert data["completed"] is False
        assert str(data["user_id"]) == str(test_user.id)
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    async def test_create_task_without_description(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Create task without description succeeds."""
        response = await client.post(
            "/api/v1/tasks",
            headers=auth_headers,
            json={"title": "Task without description"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Task without description"
        assert data["description"] is None

    async def test_create_task_without_auth(self, client: AsyncClient):
        """Create task without JWT returns 401."""
        response = await client.post(
            "/api/v1/tasks",
            json={"title": "Unauthorized Task"},
        )

        assert response.status_code == 401

    async def test_create_task_empty_title(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Create task with empty title returns 422."""
        response = await client.post(
            "/api/v1/tasks",
            headers=auth_headers,
            json={"title": ""},
        )

        assert response.status_code == 422

    async def test_create_task_title_too_long(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Create task with title > 500 chars returns 422."""
        response = await client.post(
            "/api/v1/tasks",
            headers=auth_headers,
            json={"title": "x" * 501},
        )

        assert response.status_code == 422


class TestListTasks:
    """Tests for GET /api/v1/tasks."""

    async def test_list_tasks_success(
        self, client: AsyncClient, auth_headers: dict, test_task: Task
    ):
        """List tasks returns user's tasks."""
        response = await client.get("/api/v1/tasks", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        assert len(data["tasks"]) == 1
        assert data["tasks"][0]["title"] == test_task.title

    async def test_list_tasks_empty(
        self, client: AsyncClient, auth_headers: dict
    ):
        """List tasks with no tasks returns empty list."""
        response = await client.get("/api/v1/tasks", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["tasks"] == []

    async def test_list_tasks_filter_completed(
        self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession, test_user: User
    ):
        """List tasks with completed filter works."""
        # Create completed and pending tasks
        pending = Task(user_id=test_user.id, title="Pending", completed=False)
        completed = Task(user_id=test_user.id, title="Completed", completed=True)
        db_session.add_all([pending, completed])
        await db_session.commit()

        # Filter completed=true
        response = await client.get(
            "/api/v1/tasks?completed=true", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["tasks"]) == 1
        assert data["tasks"][0]["title"] == "Completed"

        # Filter completed=false
        response = await client.get(
            "/api/v1/tasks?completed=false", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["tasks"]) == 1
        assert data["tasks"][0]["title"] == "Pending"

    async def test_list_tasks_user_isolation(
        self,
        client: AsyncClient,
        auth_headers: dict,
        other_auth_headers: dict,
        test_task: Task,
        db_session: AsyncSession,
        other_user: User,
    ):
        """Users can only see their own tasks."""
        # Create task for other user
        other_task = Task(user_id=other_user.id, title="Other User Task")
        db_session.add(other_task)
        await db_session.commit()

        # Test user should only see their task
        response = await client.get("/api/v1/tasks", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["tasks"]) == 1
        assert data["tasks"][0]["title"] == test_task.title

        # Other user should only see their task
        response = await client.get("/api/v1/tasks", headers=other_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["tasks"]) == 1
        assert data["tasks"][0]["title"] == "Other User Task"


class TestGetTask:
    """Tests for GET /api/v1/tasks/{task_id}."""

    async def test_get_task_success(
        self, client: AsyncClient, auth_headers: dict, test_task: Task
    ):
        """Get task by ID returns task data."""
        response = await client.get(
            f"/api/v1/tasks/{test_task.id}", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == test_task.title
        assert str(data["id"]) == str(test_task.id)

    async def test_get_task_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Get non-existent task returns 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await client.get(
            f"/api/v1/tasks/{fake_id}", headers=auth_headers
        )

        assert response.status_code == 404
        data = response.json()
        assert data["error"]["code"] == "NOT_FOUND"

    async def test_get_task_other_user_returns_404(
        self,
        client: AsyncClient,
        other_auth_headers: dict,
        test_task: Task,
    ):
        """Get another user's task returns 404 (not 403)."""
        response = await client.get(
            f"/api/v1/tasks/{test_task.id}", headers=other_auth_headers
        )

        # Must be 404, not 403, to prevent enumeration
        assert response.status_code == 404
        data = response.json()
        assert data["error"]["code"] == "NOT_FOUND"


class TestUpdateTask:
    """Tests for PUT /api/v1/tasks/{task_id}."""

    async def test_update_task_success(
        self, client: AsyncClient, auth_headers: dict, test_task: Task
    ):
        """Full update task returns updated data."""
        response = await client.put(
            f"/api/v1/tasks/{test_task.id}",
            headers=auth_headers,
            json={
                "title": "Updated Title",
                "description": "Updated description",
                "completed": True,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["description"] == "Updated description"
        assert data["completed"] is True
        # updated_at should be different from created_at
        assert data["updated_at"] != data["created_at"]

    async def test_update_task_other_user_returns_404(
        self,
        client: AsyncClient,
        other_auth_headers: dict,
        test_task: Task,
    ):
        """Update another user's task returns 404."""
        response = await client.put(
            f"/api/v1/tasks/{test_task.id}",
            headers=other_auth_headers,
            json={"title": "Hacked", "description": None, "completed": True},
        )

        assert response.status_code == 404


class TestPatchTask:
    """Tests for PATCH /api/v1/tasks/{task_id}."""

    async def test_patch_task_partial_update(
        self, client: AsyncClient, auth_headers: dict, test_task: Task
    ):
        """Partial update only changes provided fields."""
        original_title = test_task.title
        original_description = test_task.description

        response = await client.patch(
            f"/api/v1/tasks/{test_task.id}",
            headers=auth_headers,
            json={"completed": True},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["completed"] is True
        assert data["title"] == original_title
        assert data["description"] == original_description

    async def test_patch_task_update_title_only(
        self, client: AsyncClient, auth_headers: dict, test_task: Task
    ):
        """Patch can update title only."""
        response = await client.patch(
            f"/api/v1/tasks/{test_task.id}",
            headers=auth_headers,
            json={"title": "New Title Only"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "New Title Only"
        assert data["completed"] == test_task.completed

    async def test_patch_task_other_user_returns_404(
        self,
        client: AsyncClient,
        other_auth_headers: dict,
        test_task: Task,
    ):
        """Patch another user's task returns 404."""
        response = await client.patch(
            f"/api/v1/tasks/{test_task.id}",
            headers=other_auth_headers,
            json={"completed": True},
        )

        assert response.status_code == 404


class TestDeleteTask:
    """Tests for DELETE /api/v1/tasks/{task_id}."""

    async def test_delete_task_success(
        self, client: AsyncClient, auth_headers: dict, test_task: Task
    ):
        """Delete task returns 204 and removes task."""
        response = await client.delete(
            f"/api/v1/tasks/{test_task.id}", headers=auth_headers
        )

        assert response.status_code == 204

        # Verify task is gone
        response = await client.get(
            f"/api/v1/tasks/{test_task.id}", headers=auth_headers
        )
        assert response.status_code == 404

    async def test_delete_task_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Delete non-existent task returns 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await client.delete(
            f"/api/v1/tasks/{fake_id}", headers=auth_headers
        )

        assert response.status_code == 404

    async def test_delete_task_other_user_returns_404(
        self,
        client: AsyncClient,
        other_auth_headers: dict,
        test_task: Task,
    ):
        """Delete another user's task returns 404 (not 403)."""
        response = await client.delete(
            f"/api/v1/tasks/{test_task.id}", headers=other_auth_headers
        )

        assert response.status_code == 404


class TestUserIsolation:
    """Tests verifying multi-user data isolation."""

    async def test_user_a_cannot_see_user_b_tasks(
        self,
        client: AsyncClient,
        auth_headers: dict,
        other_auth_headers: dict,
        db_session: AsyncSession,
        test_user: User,
        other_user: User,
    ):
        """User A cannot see User B's tasks in any way."""
        # Create tasks for both users
        task_a = Task(user_id=test_user.id, title="User A Task")
        task_b = Task(user_id=other_user.id, title="User B Task")
        db_session.add_all([task_a, task_b])
        await db_session.commit()
        await db_session.refresh(task_a)
        await db_session.refresh(task_b)

        # User A lists tasks - should only see their own
        response = await client.get("/api/v1/tasks", headers=auth_headers)
        assert response.status_code == 200
        titles = [t["title"] for t in response.json()["tasks"]]
        assert "User A Task" in titles
        assert "User B Task" not in titles

        # User A tries to get User B's task directly - should get 404
        response = await client.get(
            f"/api/v1/tasks/{task_b.id}", headers=auth_headers
        )
        assert response.status_code == 404

        # User A tries to update User B's task - should get 404
        response = await client.put(
            f"/api/v1/tasks/{task_b.id}",
            headers=auth_headers,
            json={"title": "Hacked", "description": None, "completed": True},
        )
        assert response.status_code == 404

        # User A tries to delete User B's task - should get 404
        response = await client.delete(
            f"/api/v1/tasks/{task_b.id}", headers=auth_headers
        )
        assert response.status_code == 404

        # Verify User B's task still exists
        response = await client.get(
            f"/api/v1/tasks/{task_b.id}", headers=other_auth_headers
        )
        assert response.status_code == 200
        assert response.json()["title"] == "User B Task"
