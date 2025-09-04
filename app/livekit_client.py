# livekit_client.py (new module for LiveKit API client)
from livekit.api import LiveKitAPI
from .config import settings
from livekit import api


async def get_livekit_client() -> LiveKitAPI:
    """Initialize and return a LiveKitAPI client."""
    return LiveKitAPI(
        url=settings.livekit_url,
        api_key=settings.livekit_api_key,
        api_secret=settings.livekit_api_secret
    )


async def get_livekit_token(device_id: int):
    token = api.AccessToken(settings.livekit_api_key,
                        settings.livekit_api_secret) \
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
    return token