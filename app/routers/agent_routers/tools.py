from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter

from ..oauth2 import oauth2
from .. import models, schemas, utils
from typing import List, Optional
from sqlalchemy.orm import Session
from ..database import get_db
from sqlalchemy import func

router = APIRouter(
    prefix  = "/tools",
    tags = ["tools"]
)


