from fastapi import FastAPI, Response, status, HTTPException 
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from . import models
from .database import engine, SessionLocal

models.Base.metadata.create_all(bind=engine)

#Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Post(BaseModel):
    title: str
    content: str 
    published: bool = True
    rating: Optional[int] = None

    
app = FastAPI()

while True:
    try:
        conn = psycopg2.connect(host='localhost',database='FastAPIDatabase',user='postgres',
                            password='SDFKN#3j$f4', cursor_factory=RealDictCursor)
        #Realdictcurser just gives you the column names
        cursor = conn.cursor()
        print("database connection was successful")
        break
    except Exception as error:
        print("connecting to DB Failed")
        print("Error", error)
        time.sleep(3)

my_posts = [{"title": "Harry Potter", "id": 1},
            {"title": "Stranger Things","id": 2}]

def find_Post(id):
    for p in my_posts:
        if p["id"] == id:
            return p
        
def find_Index(id):
    counter = 0
    for i, p in enumerate(my_posts):
        if p["id"] == id:
            return i

@app.get("/posts")
def get_posts():
    cursor.execute("""SELECT * FROM post""")
    myposts = cursor.fetchall()
    return {'post': myposts}

#payload: dict = Body(...) is a way of importing data, but post: Post is the pydantic way 
                                                    # which brings in and validates information too
#@app.post("/posts")
#def creat_post(payload: dict = Body(...)):
#    print(payload)
#    return {"You have created a post"}


# @app.post("/posts", status_code=status.HTTP_201_CREATED)
# def creat_post(post: Post):
#     post_dict = post.dict()
#     post_dict['id'] = randrange(0,1000000)
#     my_posts.append(post_dict)
#     return {"Data": my_posts[len(my_posts)-1]}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def creat_post(post: Post):
    print(post.dict())
    cursor.execute("""INSERT INTO post (title, content, published) VALUES (%s, %s, %s) RETURNING * """, 
                   (post.title, post.content, post.published))
    new_post = cursor.fetchone() 
    conn.commit() # need to commit changes
    return {"Data": new_post}

# @app.get("/posts/{id}")
# def get_post_id(id: int, response: Response):
#     cursor.execute("""SELECT * FROM post WHERE 'id' = %s""", (id))
#     returning_post = cursor.fetchone()
#     post = find_Post(id)
#     if not post:
#         #response.status_code = 404
#         #response.status_code = status.HTTP_404_NOT_FOUND
#         #return {'message': f"Post with id: {id} was not foudn"}
#         print(id)
#         raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, 
#                             detail = f"Here is post id {id}")
#     return {"Post Detail": f"Here is post id {post['title']}"}


@app.get("/posts/{id}")
def get_post_id(id: str, response: Response):
    cursor.execute("SELECT * FROM post WHERE id = %s", (id))
    returning_post = cursor.fetchone()
    if not returning_post:
        #response.status_code = 404
        #response.status_code = status.HTTP_404_NOT_FOUND
        #return {'message': f"Post with id: {id} was not foudn"}
        print(id)
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, 
                            detail = f"Here is post id {id}")
    return {"Post Detail": returning_post}

# @app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
# def delete_posts(id: int):
#     index = find_Index(id)
#     if index == None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with {id} does not exist")
#     my_posts.pop(index)
#     return {'message': "post was successfully deleted"}
    

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_posts(id: int):
    cursor.execute("""DELETE FROM post WHERE id = %s RETURNING *""",(id,))
    deleted_Post = cursor.fetchone()
    conn.commit()
    if deleted_Post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with {id} does not exist")
    return {'message': "post was successfully deleted"}
    

# @app.put("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
# def update_post(id: int, post: Post):
#     my_post = find_Post(id)
#     if my_post == None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with {id} does not exist")
    
#     updated_post = post.dict()
#     my_post["title"] = updated_post["title"]
#     return {'message': "post was successfully deleted"}
    
@app.put("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def update_post(id: int, post: Post):
    cursor.execute("""UPDATE post SET title = %s, content = %s WHERE id = %s RETURNING * """, 
                   (post.title, post.content, id))
    updated_post = cursor.fetchone()
    conn.commit()
    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with {id} does not exist")
    
    return {'message': updated_post}
    