import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from main import Base, get_db
import models
from main import app

# Set up a test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={
                       "check_same_thread": False})
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)

# Override the get_db dependency


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope='function')
def setup_database():
    # Create the database tables
    Base.metadata.create_all(bind=engine)
    yield
    # Drop all tables
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)

# Sample user data for testing
test_user = {
    "name": "John Doe",
    "age": 30,
    "gender": "male",
    "email": "johndoe@gmail.com",
    "city": "Mumbai",
    "interests": "cricket, movies"
}

test_user_update = {
    "name": "John Updated",
    "age": 31,
    "gender": "male",
    "email": "johnupdated@gmail.com",
    "city": "Mumbai",
    "interests": "reading, sports"
}


def test_create_user(setup_database):
    response = client.post("/users/", json=test_user)
    assert response.status_code == 201
    response_data = response.json()
    assert "id" in response_data
    assert response_data["name"] == test_user["name"]
    assert response_data["email"] == test_user["email"]


def test_read_all_users(setup_database):
    response = client.get("/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)  # Ensure response is a list
    assert len(response.json()) > 0


def test_read_user(setup_database):
    response = client.post("/users/", json=test_user)
    user_id = response.json().get("id")
    assert user_id is not None
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["id"] == user_id


def test_update_user(setup_database):
    response = client.post("/users/", json=test_user)
    user_id = response.json().get("id")
    assert user_id is not None
    response = client.put(f"/users/update/{user_id}", json=test_user_update)
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["id"] == user_id
    assert response_data["name"] == test_user_update["name"]
    assert response_data["email"] == test_user_update["email"]


def test_delete_user(setup_database):
    response = client.post("/users/", json=test_user)
    user_id = response.json().get("id")
    assert user_id is not None
    response = client.delete(f"/users/delete/{user_id}")
    assert response.status_code == 202
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 404


def test_find_matches(setup_database):
    response = client.post("/users/", json=test_user)
    user_id = response.json().get("id")
    assert user_id is not None

    # Create potential matches
    test_user_2 = {
        "name": "Jane Doe",
        "age": 28,
        "gender": "female",
        "email": "janedoe@gmail.com",
        "city": "Delhi",
        "interests": "reading, music, traveling"
    }
    client.post("/users/", json=test_user_2)

    response = client.get(f"/users/matches/{user_id}")
    assert response.status_code == 200
    response_data = response.json()
    assert isinstance(response_data, list)
    assert len(response_data) > 0
