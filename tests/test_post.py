from typing import List
from app import schemas
import pytest

def test_get_all_posts(authorized_client, test_posts):
    res = authorized_client.get("/posts")
    def validate(post):
        schemas.PostOut(**post)
    post_map = map (validate, res.json())
    posts_list = list(post_map) #What is the difference between List and list
    assert res.status_code == 200
    assert len(res.json()) == len(test_posts)
    #assert posts_list[0].Post.id == test_posts[0].id #Not sure what order it goes into the db like

def test_unauthorized_user_get_all_posts(client, test_posts): # Note, dont have to have test_user as a parameter as its already being imported from the test_posts
    res = client.get("/posts/")
    assert res.status_code == 401

def test_unauthorized_user_get_one_posts(client, test_posts): # Note, dont have to have test_user as a parameter as its already being imported from the test_posts
    res = client.get(f"/posts/{test_posts[0].id}")
    assert res.status_code == 401

def test_get_one_post_not_exit(authorized_client, test_posts):
        res = authorized_client.get(f"/posts/9999")
        assert res.status_code == 404

def test_get_one_post(authorized_client, test_posts):
    res = authorized_client.get(f"/posts/{test_posts[0].id}")
    post = schemas.PostOut(**res.json())
    assert post.Post.id == test_posts[0].id
    assert post.Post.content == test_posts[0].content

@pytest.mark.parametrize("title, content, published", [
     ("awesome new title", "new content", True),
     ("great new title", "great content", False),
     ("fantastic new title", "fantastic content", True)
])
def test_create_post(authorized_client, test_user, test_posts, title, content, published):
    
    res = authorized_client.post("/posts/", json = {"title": title, "content": content, "published": published})
    #detail not found might mean the route is typed wrongs
    created_post = schemas.Post(**res.json())

    assert res.status_code == 201
    assert created_post.title == title
    assert created_post.content == content
    assert created_post.published == published
    assert created_post.user_id == test_user["id"]

def test_create_post_default_published_true(authorized_client, test_user, test_posts):
    res = authorized_client.post("/posts/", json = {"title": "title", "content": "content"})
    #detail not found might mean the route is typed wrongs
    created_post = schemas.Post(**res.json())

    assert res.status_code == 201
    assert created_post.title == "title"
    assert created_post.content == "content"
    assert created_post.published == True

def test_unauthorized_user_create_post(client, test_user, test_posts): # Note, dont have to have test_user as a parameter as its already being imported from the test_posts
    res = client.post("/posts/", json = {"title": "title", "content": "content"})
    assert res.status_code == 401

def test_unauthorized_user_delete_post(client, test_user, test_posts):
    res = client.delete(f"/posts/{test_posts[0].id}")
    assert res.status_code == 401

def test_delete_post(authorized_client, test_posts, test_user):
    res = authorized_client.delete(f"/posts/{test_posts[0].id}") #stillworks sometimes if its not an f string lol
    assert res.status_code == 204

def test_delete_post_non_exist(authorized_client, test_posts, test_user):
    res = authorized_client.delete("/posts/4534") #stillworks sometimes if its not an f string lol
    assert res.status_code == 404

def test_delete_other_user_post(authorized_client, test_posts):
    res = authorized_client.delete(f"/posts/{test_posts[3].id}") #stillworks sometimes if its not an f string lol
    assert res.status_code == 403

def test_update_post(authorized_client, test_posts, test_user):
    data = {
        "title": "updated first title",
        "content": "updated first content",
        "published": True
    }
    res = authorized_client.put(f"/posts/{test_posts[0].id}", json = data) #stillworks sometimes if its not an f string lol
    updated_post = schemas.Post(**res.json())
    assert res.status_code == 200
    assert updated_post.title == data.get("title")
    assert updated_post.content == data.get("content")



def test_update_other_user_post(authorized_client, test_posts, test_user, test_user_2):
    data = {
        "title": "updated first title",
        "content": "updated first content",
        "published": True
    }
    res = authorized_client.put(f"/posts/{test_posts[3].id}", json = data) #stillworks sometimes if its not an f string lol
    assert res.status_code ==403
    
def test_unauthorized_user_update_post(client, test_user, test_posts):
    data = {
        "title": "updated first title",
        "content": "updated first content",
        "published": True
    }
    res = client.put(f"/posts/{test_posts[0].id}", json = data)
    assert res.status_code == 401


def test_update_post_non_exist(authorized_client, test_posts, test_user):
    data = {
        "title": "updated first title",
        "content": "updated first content",
        "published": True
    }
    res = authorized_client.put("/posts/4534", json = data) #stillworks sometimes if its not an f string lol
    assert res.status_code == 404
