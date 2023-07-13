from fastapi import APIRouter, Depends, HTTPException, status
from datetime import timedelta, datetime

from models.room import RoomDisplay, RoomState, RoomDetails, Stage, Puzzle


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
            stage="Secret entrance",
            active_stage=2,
            stages=[
                Stage(
                    name="Secret entrance",
                    description="The players are searching for a button that opens the secret entrance.",
                    puzzles=[
                        Puzzle(name="Secret button", completion_worth=5, completed=True)
                    ],
                ),
                Stage(
                    name="Tablet assembly",
                    description="The players assemble a set of tablets to unlock the golden chest.",
                    puzzles=[
                        Puzzle(
                            name="Tablets",
                            completion_worth=20,
                            completed=False,
                            state={"positions": ["A", "B", None, "E", None]},
                        )
                    ],
                ),
            ],
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
            stage="Magnet fishing",
            active_stage=0,
            stages=[],
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
            stage="Sorting case files",
            active_stage=0,
            stages=[],
        ),
        RoomDetails(
            id=3,
            name="Demonic Presence",
            slug="demonic-presence",
            image_url="https://picsum.photos/seed/demonic/200",
            state=RoomState.ACTIVE,
            base_time=timedelta(hours=1, minutes=30),
            extra_time=timedelta(minutes=30),
            started_on=datetime.now() - timedelta(hours=0, minutes=20),
            stopped_on=None,
            completion=20,
            max_completion=90,
            stage="Summoning the demon",
            active_stage=3,
            stages=[
                Stage(
                    name="Stuck in cells",
                    description="The players must cooperate to extract a key using a magnet.",
                    puzzles=[
                        Puzzle(
                            name="Cells",
                            completion_worth=10,
                            completed=True,
                            state={"cellsUnlocked": [True, True]},
                        )
                    ],
                ),
                Stage(
                    name="Opening the chest",
                    description="The players must open a chest to find a crank.",
                    puzzles=[
                        Puzzle(
                            name="Chest",
                            completion_worth=5,
                            completed=True,
                        )
                    ],
                ),
                Stage(
                    name="Lowering the coffin",
                    description="The players lower the coffin.",
                    puzzles=[
                        Puzzle(
                            name="Lower the coffin",
                            completion_worth=5,
                            completed=True,
                        )
                    ],
                ),
                Stage(
                    name="Unlocking the coffin",
                    description="The players unlock the coffin using a proper button sequence.",
                    puzzles=[
                        Puzzle(
                            name="Wall buttons",
                            completion_worth=25,
                            completed=False,
                            state={"sequence": ["goat", "cow", "horse", None]},
                        )
                    ],
                ),
                Stage(
                    name="Assembling the skeleton",
                    description="The players assemble a skeleton inside the coffin.",
                    puzzles=[
                        Puzzle(
                            name="Skeleton",
                            completion_worth=10,
                            completed=False,
                            state={
                                "leftLeg": False,
                                "rightLeg": False,
                                "leftArm": False,
                                "rightArm": False,
                            },
                        )
                    ],
                ),
                Stage(
                    name="Picking up the book",
                    description="The players collect the spellbook.",
                    puzzles=[
                        Puzzle(
                            name="Spellbook",
                            completion_worth=5,
                            completed=False,
                        )
                    ],
                ),
                Stage(
                    name="Spellcasting",
                    description="The players cast summoning spells.",
                    puzzles=[
                        Puzzle(
                            name="Spell #1",
                            completion_worth=10,
                            completed=False,
                        ),
                        Puzzle(
                            name="Spell #2",
                            completion_worth=10,
                            completed=False,
                        ),
                        Puzzle(
                            name="Spell #3",
                            completion_worth=10,
                            completed=False,
                        ),
                    ],
                ),
            ],
        ),
    ]
    return rooms


@router.get("/", response_model=list[RoomDisplay])
async def index():
    return [RoomDisplay(**r.dict()) for r in create_rooms()]


@router.get("/{slug}", response_model=RoomDetails)
async def details(slug: str):
    rooms = create_rooms()
    if found_room := next((room for room in rooms if room.slug == slug), [None]):
        return found_room
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"Room {slug} not found"
    )
