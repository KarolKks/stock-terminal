import pytest
from httpx import AsyncClient

# Apply pytest async mark to all tests in this file
pytestmark = pytest.mark.asyncio


# Helper function to register and create a test user
async def create_test_user(
    ac: AsyncClient, 
    username: str = "authuser_unique", 
    email: str = "auth_unique@example.com"
):
    user_payload = {
        "username": username,
        "email": email,
        "first_name": "Auth",
        "last_name": "User",
        "password": "securepassword123"
    }
    response = await ac.post("/auth/register", json=user_payload)
    assert response.status_code == 201
    return user_payload


# Registration Tests

async def test_register_user_success(ac: AsyncClient):
    """Test successful registration with valid data."""
    user_data = {
        "username": "newuser_test",
        "email": "newuser_test@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "password": "password123"
    }
    response = await ac.post("/auth/register", json=user_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["username"] == "newuser_test"
    assert data["email"] == "newuser_test@example.com"
    assert "password" not in data
    assert "hashed_password" not in data


async def test_register_user_duplicate_username(ac: AsyncClient):
    """Test registration failure when username is taken."""
    await create_test_user(ac, username="existinguser_dup", email="existing_dup1@example.com")

    response = await ac.post("/auth/register", json={
        "username": "existinguser_dup",
        "email": "existing_dup2_unique@example.com",
        "first_name": "Jane",
        "password": "password123"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "User with this username already exists."


# Login Tests

async def test_login_success(ac: AsyncClient):
    """Test login with valid credentials returning access and refresh tokens."""
    user = await create_test_user(ac, username="loginuser_test", email="loginuser_test@example.com")

    login_data = {
        "username": user["username"],
        "password": user["password"]
    }
    response = await ac.post("/auth/login", json=login_data)
    assert response.status_code == 200
    
    tokens = response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["token_type"] == "bearer"


async def test_login_invalid_password(ac: AsyncClient):
    """Test login rejection when password is incorrect."""
    user = await create_test_user(ac, username="wrongpassuser_test", email="wrongpassuser_test@example.com")

    login_data = {
        "username": user["username"],
        "password": "invalidpassword"
    }
    response = await ac.post("/auth/login", json=login_data)
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password."


# Protected Endpoint (/auth/me) Tests

async def test_read_me_success(ac: AsyncClient):
    """Test fetching profile using a valid Bearer token."""
    user = await create_test_user(ac, username="meuser_test", email="meuser_test@example.com")

    login_resp = await ac.post("/auth/login", json={
        "username": user["username"],
        "password": user["password"]
    })
    access_token = login_resp.json()["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}
    response = await ac.get("/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["username"] == "meuser_test"


async def test_read_me_missing_token(ac: AsyncClient):
    """Test access rejection when Authorization header is omitted."""
    response = await ac.get("/auth/me")
    assert response.status_code in (401, 403)


async def test_read_me_invalid_token(ac: AsyncClient):
    """Test access rejection when an invalid or corrupted token is supplied."""
    headers = {"Authorization": "Bearer invalid_jwt_token_string"}
    response = await ac.get("/auth/me", headers=headers)
    assert response.status_code == 401
    assert "detail" in response.json()


# Refresh Token and Logout Tests

async def test_refresh_token_success(ac: AsyncClient):
    """Test exchanging a valid refresh token for a new access token."""
    user = await create_test_user(ac, username="refreshuser_test", email="refreshuser_test@example.com")

    login_resp = await ac.post("/auth/login", json={
        "username": user["username"],
        "password": user["password"]
    })
    refresh_token = login_resp.json()["refresh_token"]

    response = await ac.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    
    new_tokens = response.json()
    assert "access_token" in new_tokens
    assert new_tokens["refresh_token"] == refresh_token


async def test_logout_and_revoke_token(ac: AsyncClient):
    """Test logout invalidates the refresh token preventing further token refreshes."""
    user = await create_test_user(ac, username="logoutuser_test", email="logoutuser_test@example.com")

    login_resp = await ac.post("/auth/login", json={
        "username": user["username"],
        "password": user["password"]
    })
    refresh_token = login_resp.json()["refresh_token"]

    logout_resp = await ac.post("/auth/logout", json={"refresh_token": refresh_token})
    assert logout_resp.status_code == 200
    assert logout_resp.json()["message"] == "Successfully logged out."

    refresh_resp = await ac.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_resp.status_code == 401
    assert refresh_resp.json()["detail"] == "Invalid or revoked refresh token."