"""The :mod:`app.tests.test_auth.` module contains tests for authentication on serenity's corporate care APIs
"""
# Author: Christopher Dare

### Test cases
# Should be able to login via oauth2 existing users

import logging

from app.api.deps import get_db as get_session
from app.main import app
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from tests.conftest import new_user_credentials, user_signup_payload, test_client

# set log level to debug
logging.basicConfig(level=logging.INFO)


def test_can_user_login(new_user_credentials, test_client):
    client = test_client
    user_create_endpoint = "/v1/auth/login/access-token"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }

    response = client.post(user_create_endpoint, headers=headers, data=new_user_credentials)

    logging.info(f"User login response content: {response.content}")

    assert response.status_code == 200
    assert "access_token" in response.json()