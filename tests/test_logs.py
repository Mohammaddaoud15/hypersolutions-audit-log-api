from uuid import uuid4

from app.core.auth import hash_password
from app.models import User, UserRole


def get_token(client, username):
    response = client.post(
        "/auth/login",
        data={
            "username": username,
            "password": "password123",
        },
    )
    return response.json()["access_token"]


def create_test_user(db, username: str, role: str = "User"):
    db_user = User(
        username=username,
        hashed_password=hash_password("password123"),
        role=UserRole(role)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def test_create_audit_log(client, db):
    user = create_test_user(db, "testuser")
    token = get_token(client, "testuser")

    response = client.post(
        "/logs/",
        json={
            "action": "READ",
            "resource_type": "User",
            "resource_id": "123",
            "status": "SUCCESS",
            "details": {"test": "value"},
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["action"] == "READ"
    assert data["resource_type"] == "User"
    assert data["resource_id"] == "123"
    assert data["status"] == "SUCCESS"
    assert data["details"] == {"test": "value"}
    assert data["user_id"] == str(user.id)


def test_get_own_logs(client, db):
    user = create_test_user(db, "testuser")
    token = get_token(client, "testuser")

    client.post(
        "/logs/",
        json={
            "action": "READ",
            "resource_type": "User",
            "resource_id": "123",
            "status": "SUCCESS",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    response = client.get(
        "/logs/",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["user_id"] == str(user.id)


def test_get_nonexistent_log(client, db):
    create_test_user(db, "testuser")
    token = get_token(client, "testuser")

    response = client.get(
        f"/logs/{uuid4()}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404
    assert "was not found" in response.json()["detail"]


def test_user_cannot_view_another_users_log(client, db):
    create_test_user(db, "user1")
    create_test_user(db, "user2")

    token1 = get_token(client, "user1")
    token2 = get_token(client, "user2")

    create_response = client.post(
        "/logs/",
        json={
            "action": "READ",
            "resource_type": "User",
            "resource_id": "123",
            "status": "SUCCESS",
        },
        headers={"Authorization": f"Bearer {token1}"},
    )

    log_id = create_response.json()["id"]

    response = client.get(
        f"/logs/{log_id}",
        headers={"Authorization": f"Bearer {token2}"},
    )

    assert response.status_code == 403


def test_admin_can_view_another_users_log(client, db):
    create_test_user(db, "user1")
    create_test_user(db, "admin_user", role="Admin")

    token1 = get_token(client, "user1")
    admin_token = get_token(client, "admin_user")

    create_response = client.post(
        "/logs/",
        json={
            "action": "READ",
            "resource_type": "User",
            "resource_id": "123",
            "status": "SUCCESS",
        },
        headers={"Authorization": f"Bearer {token1}"},
    )

    log_id = create_response.json()["id"]

    response = client.get(
        f"/logs/{log_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    assert response.json()["id"] == log_id


def test_get_logs_with_action_filter(client, db):
    create_test_user(db, "testuser")
    token = get_token(client, "testuser")

    client.post(
        "/logs/",
        json={
            "action": "READ",
            "resource_type": "User",
            "resource_id": "1",
            "status": "SUCCESS",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    client.post(
        "/logs/",
        json={
            "action": "WRITE",
            "resource_type": "User",
            "resource_id": "2",
            "status": "SUCCESS",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    response = client.get(
        "/logs/search?action=READ",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["action"] == "READ"


def test_get_log_by_id(client, db):
    create_test_user(db, "testuser")
    token = get_token(client, "testuser")

    create_response = client.post(
        "/logs/",
        json={
            "action": "READ",
            "resource_type": "User",
            "resource_id": "123",
            "status": "SUCCESS",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    log_id = create_response.json()["id"]

    response = client.get(
        f"/logs/{log_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["id"] == log_id
