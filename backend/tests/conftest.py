"""The :mod:`tests.fixtures` module fixtures used for testing
"""
import pytest
from typing import Generator, List

from app.api import deps
from app.api.deps import get_db as get_session
from app.main import app
from app.core.session import async_db_url
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool



@pytest.fixture(scope='session')
def test_client() -> Generator[TestClient, None, None]:
    """
    TODO: Overrides the normal database access with test database,
    and yields a configured test client
    """

    # app.dependency_overrides[deps.get_db] = lambda: db_session

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def user_signup_payload():
    yield {
        "mobile": "+233506409457",
        "first_name": "Test",
        "last_name": "User",
        "password": "qG1IN0kHLKYQGGT",
    }


@pytest.fixture
def new_user_credentials():
    yield {
        "username": "+233506409457",
        "password": "qG1IN0kHLKYQGGT",
        "scope": "current_user:read",
    }

