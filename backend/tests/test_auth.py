"""Tests for authentication endpoints."""

import pytest
from httpx import AsyncClient

from models import User


class TestRegister:
    """Tests for POST /api/v1/auth/register."""

    async def test_register_success(self, client: AsyncClient):
        """Register new user returns 201 with user data and JWT."""
        response = await client.post(
            "/api/v1/auth/register",
            json={"email": "new@example.com", "password": "password123"},
        )

        assert response.status_code == 201
        data = response.json()
        assert "user" in data
        assert "token" in data
        assert data["user"]["email"] == "new@example.com"
        assert "id" in data["user"]
        assert "created_at" in data["user"]
        assert len(data["token"]) > 0

    async def test_register_duplicate_email(self, client: AsyncClient, test_user: User):
        """Register with existing email returns 409 Conflict."""
        response = await client.post(
            "/api/v1/auth/register",
            json={"email": test_user.email, "password": "password123"},
        )

        assert response.status_code == 409
        data = response.json()
        assert data["error"]["code"] == "CONFLICT"
        assert "already registered" in data["error"]["message"].lower()

    async def test_register_invalid_email(self, client: AsyncClient):
        """Register with invalid email returns 422."""
        response = await client.post(
            "/api/v1/auth/register",
            json={"email": "not-an-email", "password": "password123"},
        )

        assert response.status_code == 422

    async def test_register_short_password(self, client: AsyncClient):
        """Register with password < 8 chars returns 422."""
        response = await client.post(
            "/api/v1/auth/register",
            json={"email": "new@example.com", "password": "short"},
        )

        assert response.status_code == 422

    async def test_register_missing_fields(self, client: AsyncClient):
        """Register with missing fields returns 422."""
        response = await client.post(
            "/api/v1/auth/register",
            json={"email": "new@example.com"},
        )

        assert response.status_code == 422


class TestLogin:
    """Tests for POST /api/v1/auth/login."""

    async def test_login_success(self, client: AsyncClient, test_user: User):
        """Login with valid credentials returns 200 with user data and JWT."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "password123"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert "token" in data
        assert data["user"]["email"] == test_user.email
        assert str(data["user"]["id"]) == str(test_user.id)

    async def test_login_wrong_password(self, client: AsyncClient, test_user: User):
        """Login with wrong password returns 401 with generic message."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "wrongpassword"},
        )

        assert response.status_code == 401
        data = response.json()
        assert data["error"]["code"] == "UNAUTHORIZED"
        assert "invalid credentials" in data["error"]["message"].lower()

    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Login with non-existent email returns 401 with generic message."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "nonexistent@example.com", "password": "password123"},
        )

        assert response.status_code == 401
        data = response.json()
        assert data["error"]["code"] == "UNAUTHORIZED"
        # Same message as wrong password to prevent enumeration
        assert "invalid credentials" in data["error"]["message"].lower()

    async def test_login_missing_fields(self, client: AsyncClient):
        """Login with missing fields returns 422."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com"},
        )

        assert response.status_code == 422


class TestJWTValidation:
    """Tests for JWT token validation."""

    async def test_protected_endpoint_with_valid_token(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Protected endpoint accepts valid JWT."""
        response = await client.get("/api/v1/tasks", headers=auth_headers)

        assert response.status_code == 200

    async def test_protected_endpoint_without_token(self, client: AsyncClient):
        """Protected endpoint without token returns 401."""
        response = await client.get("/api/v1/tasks")

        assert response.status_code == 401
        data = response.json()
        assert data["error"]["code"] == "UNAUTHORIZED"

    async def test_protected_endpoint_with_invalid_token(self, client: AsyncClient):
        """Protected endpoint with invalid token returns 401."""
        response = await client.get(
            "/api/v1/tasks",
            headers={"Authorization": "Bearer invalid.token.here"},
        )

        assert response.status_code == 401

    async def test_protected_endpoint_with_malformed_header(self, client: AsyncClient):
        """Protected endpoint with malformed auth header returns 401."""
        response = await client.get(
            "/api/v1/tasks",
            headers={"Authorization": "NotBearer token"},
        )

        assert response.status_code == 401
