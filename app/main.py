from fastapi import FastAPI
from . import models
from .database import engine
from .routers.user_routers import post, user, authentication, vote, device
from .routers.agent_routers import tools
from .routers.device_routers import device_authenticate
from .config import settings
from fastapi.middleware.cors import CORSMiddleware

#uvicorn app.main:app --reload 

# Dont really need the following, now  we have alembic
models.Base.metadata.create_all(bind=engine)

    
app = FastAPI()

#origins = ["https://www.google.com.au"]
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(vote.router)
app.include_router(post.router)
app.include_router(user.router)
app.include_router(authentication.router)
app.include_router(tools.router)
app.include_router(device.router)
app.include_router(device_authenticate.router)

@app.get("/")
def get_posts(): 
    return {"Message": "Correctly deployed on Heroku"}




        


