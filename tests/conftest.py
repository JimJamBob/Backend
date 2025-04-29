#Automatically imported into every file in the test folder
# To run individual test, go pytest -v -s tests/test_vote.py

from fastapi.testclient import TestClient
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.main import app
from app import schemas
from app.config import settings
from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.database import get_db, Base
from app.oauth2 import create_access_token
from app import models

import pytest
from alembic import command

# 'postgresql://<username>:<password>@<hostname>/<database_name>'  Add _test to change the name of the database
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}_test" #for override

engine = create_engine(SQLALCHEMY_DATABASE_URL) #for override

Testing_SessionLocal = sessionmaker(autocommit=False, autoflush = False, bind = engine) #for override




@pytest.fixture()  #Run before every function
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = Testing_SessionLocal()
    try:
        yield db
    finally:
        db.close() 

@pytest.fixture()  #Run before every function
def client(session):
    def Override_get_db():
        try:
            yield session
        finally:
            session.close() 
    app.dependency_overrides[get_db] = Override_get_db #for override

    yield TestClient(app) #This is where we create our test client now


@pytest.fixture()  
def test_user(client):
    user_data = {
        "email": "Michael@gmail.com",
        "password": "password"
        }
    res = client.post("/users/", json = user_data)
    new_user = res.json()
    new_user["password"] = user_data.get("password")
    assert res.status_code == 201
    return new_user

@pytest.fixture()  
def test_user_2(client):
    user_data = {
        "email": "James@gmail.com",
        "password": "password"
        }
    res = client.post("/users/", json = user_data)
    new_user = res.json()
    new_user["password"] = user_data.get("password")
    assert res.status_code == 201
    return new_user

@pytest.fixture()  
def token(test_user):
    return create_access_token({"user_id": test_user.get("id")})

@pytest.fixture()  
def authorized_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    return client #so we are just taking the client, adding a header with token, and returing the client


@pytest.fixture()  
def test_posts(test_user, test_user_2, session):
    posts_data = [{
        "title": "first title",
        "content": "first content",
        "user_id": test_user['id']
        }, {
        "title": "2nd title",
        "content": "2nd content",
        "user_id": test_user['id']
        },
        {
        "title": "3rd title",
        "content": "3rd content",
        "user_id": test_user_2['id']
        }, {
        "title": "4th title",
        "content": "4th content",
        "user_id": test_user_2['id']
        }]
    def create_post_model(post):
        return models.Post(**post)

    post_map = map(create_post_model, posts_data)
    posts = list(post_map)
    posts = session.add_all(posts)
    print(posts)
    # session.add_all([models.Post(title="first title", content="first content", owner_id=test_user['id']),
    #                 models.Post(title="2nd title", content="2nd content", owner_id=test_user['id']), models.Post(title="3rd title", content="3rd content", owner_id=test_user['id'])])
    session.commit()
    posts = session.query(models.Post).all()


    return posts

