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

@router.post("/deactivate", status_code=status.HTTP_201_CREATED, response_model= schemas.DeviceID)
async def deactivate(device_id: schemas.DeviceID, db: Session = Depends(get_db), lkapi: LiveKitAPI = Depends(get_livekit_client), 
                      current_user_id: int = Depends(oauth2.get_current_user)):

    # Fetch the device by ID
    device = db.query(models.Device).filter(models.Device.device_id == device_id.device_id).first()


    if device:
        device.marked_active = False  # Update column value
        db.commit()                   # Save changes to DB
        db.refresh(device)            # Refresh object with updated values
        
        # Try to delete the LiveKit room if it exists
        try:
            await lkapi.room.delete_room(DeleteRoomRequest(
                room=f"{device_id.device_id}",
            ))
            print(f"Successfully deleted LiveKit room for device {device_id.device_id}")
        except Exception as e:
            # Room probably doesn't exist or other LiveKit error
            # Log the error but don't fail the deactivation
            print(f"Could not delete LiveKit room for device {device_id.device_id}: {str(e)}")
            # Optionally log with proper logging:
            # logger.warning(f"Could not delete LiveKit room for device {device_id.device_id}: {str(e)}")
        
        return device
    else:
        raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Device not found"
    )


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=schemas.DeviceID)
async def register_device(device_id: schemas.DeviceID, db: Session = Depends(get_db), 
                         current_user_id: int = Depends(oauth2.get_current_user)):
    
    # Check if device already exists
    existing_device = db.query(models.Device).filter(
        models.Device.device_id == device_id.device_id
    ).first()
    
    if existing_device:
        # Device exists - check if it's not marked as assigned
        if not existing_device.marked_assigned:
            # Update existing device with user and mark as assigned
            existing_device.user_id = current_user_id
            existing_device.marked_assigned = True
            existing_device.marked_active = True  # Ensure it's active
            
            db.commit()
            db.refresh(existing_device)
            
            return existing_device
        else:
            # Device already assigned to someone
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Device {device_id.device_id} is already assigned to a user"
            )
    else:
        # Device doesn't exist - create new device
        new_device = models.Device(
            device_id=device_id.device_id,
            user_id=current_user_id,
            marked_assigned=True,
            marked_active=True
        )
        
        db.add(new_device)
        db.commit()
        db.refresh(new_device)
        
        return new_device
    
@router.get("/getdevices")
async def get_all_devicese(db: Session = Depends(get_db), 
                         current_user_id: int = Depends(oauth2.get_current_user)):
    devices = db.query(models.Device).all()
    return devices
    
    



