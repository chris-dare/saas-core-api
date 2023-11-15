"""The :mod:`app.tests.test_users.` module contains tests for user management on serenity
"""
# Author: Christopher Dare

### Test cases
# Creating a user without an email or mobile should fail
# Creating a user with either an email or mobile should pass
# After creating a user, the user must own an organization and be a member of that organization

import logging

from app.api.deps import get_db as get_session
from app.main import app
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

# set log level to debug
logging.basicConfig(level=logging.INFO)


def get_testing_app(
    override_db: bool = True,
):
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


def test_onboard_user():
    # Sign up a user with only their first and last name, plus their mobile number
    client = TestClient(get_testing_app())
    user_create_endpoint = "/v1/users/sign-up"

    payload = {
        "first_name": "Test",
        "last_name": "User",
        "mobile": "+2348030000000",
    }

    response = client.post(user_create_endpoint, json=payload)

    logging.info(f"Create user response: {response.json()}")

    # test user sign up with duplicate mobile number

    assert response.status_code == 200

    payload = {
        "first_name": "Test",
        "last_name": "User",
        "mobile": "+2348030000000",
    }

    response = client.post(user_create_endpoint, json=payload)

    logging.info(f"Create duplicate user response: {response.json()}")

    app.dependency_overrides.clear()

    assert response.status_code == 400
