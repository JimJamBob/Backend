from typing import List
from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session

from app.database import get_db

from .. import oauth2
from .. import database, schemas, models, utils
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from livekit import api
import os
from livekit.api import lkapi

router = APIRouter(
    tags = ["Device Authenication"],
    prefix  = "/device_authentication"
    )


#The following endpoint takes the backend jwt and provides the livekit jwt 
@router.post('/', response_model= schemas.Token)
async def get_livekit_token(device_id: schemas.DeviceID 
                    ,db: Session = Depends(get_db), current_user: int = 
                        Depends(oauth2.get_current_user)):
    
    # Check if the user has the device and if its not flagged
    device = db.query(models.Device).filter(
        models.Device.user_id == current_user.id,
        models.Device.device_id == device_id
    ).first()

    if device is None or device.marked_active == False:
        return None  # or raise an exception
    
    #CHecked that the device isn't flagged lost, and the user exists and it logged in. Now create room
    #Use the device name as the room is better, as it requires less db queries.
    room = await lkapi.room.create_room(CreateRoomRequest(
        name=f"{device_id}",
        empty_timeout=10 * 60,
        max_participants=2,
        ))
    
    #With name room, is where the device can only join the room above.
    livekit_token = api.AccessToken(os.getenv('LIVEKIT_API_KEY'),
                        os.getenv('LIVEKIT_API_SECRET')) \
        .with_identity("identity") \
        .with_name("name") \
        .with_grants(api.VideoGrants(
            room_join=True,
            room=f"{device_id}")) \
            .with_room_config(
                api.RoomConfiguration(
                    agents=[
                        api.RoomAgentDispatch(
                            agent_name="test-agent", metadata="test-metadata"
                        )
                    ],
                ),
            ).to_jwt()

    
    return {"access_token": livekit_token, "token_type": "Bearer"}
