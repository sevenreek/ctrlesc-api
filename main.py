from fastapi import FastAPI
from mqtt import mqtt

from routes.rooms import router as room_router

app = FastAPI()
# mqtt.init_app(app)

app.include_router(room_router)


@app.get("/")
async def index():
    return "Hello world!"
