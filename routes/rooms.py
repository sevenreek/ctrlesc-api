from fastapi import APIRouter, Depends, HTTPException, status
from datetime import timedelta, datetime 

from models.room import RoomDisplay, RoomState, RoomDetails


router = APIRouter(prefix="/rooms", tags=["rooms"])


def create_rooms():
    rooms = [
        RoomDetails(
            id=0,
            name="Maian Temple",
            slug="maian-temple",
            image_url="https://picsum.photos/seed/maian/200",
            state=RoomState.READY,
            base_time=timedelta(minutes=10),
            started_on=datetime.now() - timedelta(minutes=1),
        ),
        RoomDetails(
            id=1,
            name="Atlantis Expedition",
            slug="atlantis-expedition",
            image_url="https://picsum.photos/seed/atlantis/200",
            state=RoomState.ACTIVE,
            base_time=timedelta(minutes=10),
            extra_time=timedelta(minutes=15),
            started_on=datetime.now() - timedelta(minutes=8),
            completion=28,
        ),
        RoomDetails(
            id=2,
            name="Noir Detective",
            slug="noir-detective",
            image_url="https://picsum.photos/seed/noir/200?greyscale",
            state=RoomState.ACTIVE,
            base_time=timedelta(minutes=30),
            extra_time=timedelta(minutes=5),
            started_on=datetime.now() - timedelta(minutes=25),
            completion=76,
            max_completion=149,
        ),
        RoomDetails(
            id=3,
            name="Demonic Presence",
            slug="demonic-presence",
            image_url="https://picsum.photos/seed/demonic/200",
            state=RoomState.FINISHED,
            base_time=timedelta(hours=1, minutes=30),
            extra_time=timedelta(minutes=0),
            started_on=datetime.now() - timedelta(hours=1, minutes=12),
            stopped_on=datetime.now() - timedelta(minutes=8),
            completion=45,
            max_completion=45,
        ),
    ]
    return rooms


@router.get("/", response_model=list[RoomDisplay])
async def index():
    return [RoomDisplay(**r.dict()) for r in create_rooms()]


@router.get("/{slug}", response_model=RoomDetails)
async def details(slug: str):
    rooms = create_rooms()
    if found_room := next(
        (room for room in rooms if room.slug == slug), [None]
    ):
        return found_room
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Room {slug} not found"
    )
