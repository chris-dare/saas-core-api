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

import logging

# set log level to debug
logging.basicConfig(level=logging.INFO)


def get_testing_app(override_db: bool = True,):
    if override_db:
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

        def get_session_override():
            return session

        app.dependency_overrides[get_session] = get_session_override
    return app

def test_create_patient_user():
    # Sign up a user with only their first and last name, plus their mobile number
    client = TestClient(get_testing_app())
    user_create_endpoint = "/v1/users/sign-up"

    payload = {
        "first_name": "Test",
        "last_name": "User",
        "mobile": "+2348030000000",
    }

    response = client.post(
        user_create_endpoint, json=payload
    )

    app.dependency_overrides.clear()

    logging.info(f"Create user response: {response.json()}")

    assert response.status_code == 200