from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session

from ... import oauth2
from ... import schemas, models, utils
from ...database import get_db
from ...livekit_client import get_livekit_client
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from livekit.api import LiveKitAPI

from fastapi import HTTPException, status

from livekit.api import DeleteRoomRequest


router = APIRouter(
    prefix  = "/device",
    tags = ["device"]
)

@router.post("/deactivate", status_code=status.HTTP_201_CREATED, response_model= schemas.Device)
async def deactivate(device: schemas.Device, db: Session = Depends(get_db), lkapi: LiveKitAPI = Depends(get_livekit_client), 
                      current_user_id: int = Depends(oauth2.get_current_user)):

    # Fetch the device by ID
    device = db.query(models.Device).filter(models.Device.device_id == device.device_id).first()


    if device:
        device.marked_active = False  # Update column value
        db.commit()                   # Save changes to DB
        db.refresh(device)            # Refresh object with updated values
        
        # Try to delete the LiveKit room if it exists
        try:
            await lkapi.room.delete_room(DeleteRoomRequest(
                room=f"{device.device_id}",
            ))
            print(f"Successfully deleted LiveKit room for device {device.device_id}")
        except Exception as e:
            # Room probably doesn't exist or other LiveKit error
            # Log the error but don't fail the deactivation
            print(f"Could not delete LiveKit room for device {device.device_id}: {str(e)}")
            # Optionally log with proper logging:
            # logger.warning(f"Could not delete LiveKit room for device {device.device_id}: {str(e)}")
        
        return device
    else:
        raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Device not found"
    )

    

@router.post("/deactivate", status_code=status.HTTP_201_CREATED, response_model= schemas.Device)
async def activate(device: schemas.Device, db: Session = Depends(get_db), 
                      current_user_id: int = Depends(oauth2.get_current_user)):

    # Fetch the device by ID
    device = db.query(models.Device).filter(models.Device.device_id == device.device_id).first()


    if device:
        device.marked_active = True   # Update column value
        db.commit()                   # Save changes to DB
        db.refresh(device)            # Refresh object with updated values
        
        return device
    else:
        raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Device not found"
    )


#This endpoint registers a device. Call this to assign it to a user. User may be generic admin out of the factory.
#Interesting route because it requires password, and also asks for JWT authorisation, but makes sense.
#This end point will be for pairing
@router.post("/register/{device_id}", status_code=status.HTTP_201_CREATED, response_model=schemas.Token)
async def register_device(device_id: int,
                            user_credentials: OAuth2PasswordRequestForm = Depends(),
                                db: Session = Depends(get_db),
                                    current_user_id: int = Depends(oauth2.get_current_user)):
    

    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()
    if not user:
        #Dont tell them whether the email or the password were incorrect
        print("Email Wrong")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")
    
    if not utils.verify(user_credentials.password, user.password):
        print("Password Wrong")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")
    

    # Check if device already exists
    existing_device = db.query(models.Device).filter(models.Device.device_id == device_id).first()

    if not existing_device:
        #All devices coming out of the factory should be in the db
        print("Device does exist")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")


    #If its not active, mark it active. Only if its registered to the current user
    if not existing_device.marked_active:
        if existing_device.user_id is current_user_id:
            existing_device.marked_active = True
            db.commit()
            db.refresh(existing_device)
        else:
            # Device already assigned and active
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Device {device_id} is flagged_unactive, unable to connect"
                )
    if existing_device.user_id is None:
        # Update existing device with user and mark as assigned
        existing_device.user_id = current_user_id
        existing_device.marked_assigned = True
        existing_device.marked_active = True  # Ensure it's active
            
        db.commit()
        db.refresh(existing_device)
            
            
    elif existing_device.user_id is not user.id:
        # Device assigned to someone else and active
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Device {device_id} is already assigned, must unassign"
        ) 

        
    device_access_token = oauth2.create_device_access_token(data = {"user_id": user.id, "device_id": device_id})
    
    return {"access_token": device_access_token, "token_type": "Bearer"}

          
    
@router.get("/getdevices")
async def get_all_devicese(db: Session = Depends(get_db), 
                         current_user_id: int = Depends(oauth2.get_current_user)):
    devices = db.query(models.Device).all()
    return devices
    
    



