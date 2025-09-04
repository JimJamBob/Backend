from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter

from ... import oauth2
from ... import models, schemas, utils
from typing import List, Optional
from sqlalchemy.orm import Session
from ...database import get_db
from sqlalchemy import func

router = APIRouter(
    prefix  = "/posts",
    tags = ["posts"]
)


#@router.get("/", response_model= List[schemas.Post])
@router.get("/", response_model= List[schemas.PostOut])
def get_posts(db: Session = Depends(get_db), current_user: int = 
                Depends(oauth2.get_current_user), limit: int  = 10, skip: int = 0,
                    search: Optional[str] = ""):
    posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()

    #without specifying outer, it is automattically inner, but in postgres it is automatiically inner
    results = db.query(models.Post, func.count(models.Vote.post_id).label("Votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter = True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(
            limit).offset(skip).all()
    
    return results




@router.post("/", status_code=status.HTTP_201_CREATED, response_model= schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db), current_user_id: int = 
                Depends(oauth2.get_current_user)):

    #Creating a new instance of a post class in the models file
    #new_post = models.Post(title=post.title, content = post.content, published = post.published)

    #post = post.dict()
    #post.update({"user_id": current_user_id})
    new_post = models.Post(user_id = current_user_id ,**post.dict())
    #Adding the instance of the class/relation Post to the db within the relation Post
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post




@router.get("/{id}", response_model= schemas.PostOut)
def get_post_id(id: int, db: Session = Depends(get_db), current_user: int = 
                Depends(oauth2.get_current_user)):
    returning_post = db.query(models.Post, func.count(models.Vote.post_id).label("Votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter = True).group_by(models.Post.id).filter(models.Post.id == id).first()
    
    if not returning_post:
        print(id)
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, 
                            detail = f"Here is post id {id}")
    return returning_post




@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_posts(id: int, db: Session = Depends(get_db),current_user: int = 
                Depends(oauth2.get_current_user)):
    #When deleting, you dont retreive the post, you just retreive the SQL object, 
    # then that object has a delete attribute, so no first() or all()

    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()



    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with {id} does not exist")
    
    if post.user_id != current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"This is not your post")


    post_query.delete(synchronize_session = False)
    db.commit()
    return {'message': 'successful'}
    

@router.put("/{id}", status_code=status.HTTP_200_OK, response_model= schemas.Post)
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db),current_user: int = 
                Depends(oauth2.get_current_user)):
    
    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with {id} does not exist")
    
    if post.user_id != current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"This is not your post")


    #post_querry.update({'title': 'updated title', 'content': 'updated content'}, synchronize_session=False)
    post_query.update(updated_post.dict(), synchronize_session=False)

    db.commit()
    
    
    return post_query.first()
    