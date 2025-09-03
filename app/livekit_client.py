import os
from livekit.api import LiveKitAPI
from .config import settings

lkapi = LiveKitAPI(
    api_key=os.getenv({settings.livekit_api_key}),
    api_secret=os.getenv({settings.livekit_api_secret}),
)
