from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from .. import models, schemas, utils, oauth2
from typing import List
from sqlalchemy.orm import Session
from ..database import get_db


router = APIRouter(
    prefix  = "/vote",
    tags = ["Vote"]

)



@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(vote: schemas.Vote, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    post = db.query(models.Post).filter(models.Post.id==vote.post_id).first()
    if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = f"Post with id {vote.post_id} does not exist")

    vote_query = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id, models.Vote.user_id == current_user)
    found_vote = vote_query.first()

    if (vote.dir == 1):
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail = f"User has already voted on post with id of {vote.post_id}")
        new_vote = models.Vote(post_id = vote.post_id, user_id = current_user)
        db.add(new_vote)
        db.commit()
        return{"message": "Successfuly added vote"}    
    else:
        if not found_vote:
            print("what the heeel")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = f"Post does not exist")
        vote_query.delete(synchronize_session=False)
        db.commit()

        return{"message": "Successfuly deleted vote"}    

