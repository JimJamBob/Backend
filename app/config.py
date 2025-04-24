from pydantic_settings import BaseSettings

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

    class Config: 
        env_file = ".env"

settings = Settings()
