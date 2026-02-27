from app.services.auth_service import hash_password, verify_password


def test_password_hash_and_verify() -> None:
    password = "super-secret-123"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong-password", hashed)
