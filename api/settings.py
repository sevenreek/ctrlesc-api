from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    room_config_dir: str = "./public/config/rooms"
    redis_url: str = "localhost"
    redis_port: str = "6379"
    mqtt_url: str = "localhost"
    mqtt_port: str = "1883"
    db_user: str = "postgres"
    db_password: str = "masterkey"
    db_host: str = "localhost:5555"
    db_name: str = "postgres"


settings = Settings()
