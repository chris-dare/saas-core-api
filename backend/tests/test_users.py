"""The :mod:`app.tests.test_users.` module contains tests for user management on serenity
"""
# Author: Christopher Dare

### Test cases
# Creating a user without an email or mobile should fail
# Creating a user with either an email or mobile should pass
# After creating a user, the user must own an organization and be a member of that organization

from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.main import app
from app.api.deps import get_db as get_session


def test_create_user():
    engine = create_engine(
        "sqlite://",  #
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  #
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        def get_session_override():
            return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    user_create_endpoint = "/v2/patient-portal/users/sign-up"

    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    payload = {
        "first_name": "Test",
        "last_name": "User",
        "email": "test-user23@example.com",
        "mobile": "+2348030000000",
        "password": "go tigers"
    }

    response = client.post(
        user_create_endpoint, json=payload
    )

    app.dependency_overrides.clear()

    assert response.status_code == 200