from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    room_config_dir: str = "./public/config/rooms"
    redis_url: str = "localhost"
    redis_port: str = "6379"
    mqtt_url: str = "localhost"
    mqtt_port: str = "1883"


settings = Settings()
