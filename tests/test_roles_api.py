import pytest


@pytest.mark.asyncio
async def test_roles_check_requires_auth(client) -> None:
    check_response = await client.get(
        "/api/roles/check",
        params={"user_id": "u", "app_key": "tripod-studio", "role_key": "admin"},
    )

    assert check_response.status_code == 401
    data = check_response.json()
    assert "detail" in data
    assert data.get("code") == "UNAUTHORIZED"
