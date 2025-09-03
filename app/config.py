from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    #Env variables are usuall capitaised, but in pydantic it will flatten them all
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    livekit_access_token_expire_minutes: int
    
    livekit_url: str
    livekit_api_secret: str
    livekit_api_key: str


    class Config: 
        env_file = ".env"


settings = Settings()
print("Working directory:", os.getcwd())
print("Loaded database name:", settings.database_name)

