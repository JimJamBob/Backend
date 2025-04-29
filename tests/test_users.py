import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.main import app
from app import schemas
from app.config import settings
#from database import client, session
import pytest
from jose import jwt



# def test_root(client):
#     res = client.get("/")#Why do we pass this in instead of localhost
#     print(res.json().get("Message"))
#     assert res.json().get("Message") == "Hello World"
#     assert res.status_code == 200

def test_create_user(client):
    #Make sure to add trailing slash because http... redirects to http../
    res = client.post("/users/", json={
        "email": "Michael@gmail.com",
        "password" : "password"
        }) #Sending data in the body
    print(res.json())
    new_user = schemas.UserConfirmation(**res.json()) #Doesnt validate whether these are the right values, just whter the right types of values are there
    #assert res.json().get("email") == "Michael@gmail.com"
    assert new_user.email == "Michael@gmail.com"
    assert res.status_code == 201

def test_login(client, test_user):
    res = client.post("/login",data={
        "username": test_user.get("email"), # has to be username coz of oauth2login function
        "password": test_user.get("password")
    })
    login_res = schemas.Token(**res.json())

    payload = jwt.decode(login_res.access_token, settings.secret_key, algorithms=[settings.algorithm])
    id = payload.get("user_id")
    assert id == test_user["id"] #same as test_user.get("id")
    assert login_res.token_type == "Bearer"
    assert res.status_code==200

@pytest.mark.parametrize("email, password, status_code", [
    ("wrong_email", "password", 403),
    ("Michael@gmail.com", "wrong_password", 403),
    ("wrong_email", "wrong_password", 403),
    ("Michael@gmail.com", None, 403) #None still prints as "None" which is a 403 still, not 422
])
def test_incorrect_login(client,email, password, status_code):
    res = client.post("/login", data = {"username": email, "password": password})
    print(res.status_code)
    assert res.status_code == status_code
    #assert res.json().get("detail") == "Invalid Credentials"