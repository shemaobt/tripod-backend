import pytest


@pytest.mark.asyncio
async def test_signup_login_and_me_flow(client) -> None:
    signup_response = await client.post(
        "/api/auth/signup",
        json={"email": "alice@example.com", "password": "super-secret-123", "display_name": "Alice"},
    )
    assert signup_response.status_code == 201

    login_response = await client.post(
        "/api/auth/login",
        json={"email": "alice@example.com", "password": "super-secret-123"},
    )
    assert login_response.status_code == 200

    access_token = login_response.json()["tokens"]["access_token"]
    me_response = await client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "alice@example.com"
