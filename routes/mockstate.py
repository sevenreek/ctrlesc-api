from api.models.rooms import RoomStateDetails, StageState, PuzzleState
from api.models.base import TimerState
from datetime import datetime, timedelta


def mock_room():
    return RoomStateDetails(
        slug="demonic-presence",
        state=TimerState.ACTIVE,
        extra_time=timedelta(minutes=30),
        started_on=datetime.now() - timedelta(hours=1, minutes=40),
        stopped_on=None,
        completion=20,
        active_stage=3,
        stages=[
            StageState(
                name="Stuck in cells",
                puzzles=[
                    PuzzleState(
                        name="Cells",
                        completion_worth=10,
                        completed=True,
                        state={"cellsUnlocked": [True, True]},
                    )
                ],
            ),
            StageState(
                name="Opening the chest",
                puzzles=[
                    PuzzleState(
                        name="Chest",
                        completion_worth=5,
                        completed=True,
                    )
                ],
            ),
            StageState(
                name="Lowering the coffin",
                description="The players lower the coffin.",
                puzzles=[
                    PuzzleState(
                        name="Lower the coffin",
                        completion_worth=5,
                        completed=True,
                    )
                ],
            ),
            StageState(
                name="Unlocking the coffin",
                description="The players unlock the coffin using a proper button sequence.",
                puzzles=[
                    PuzzleState(
                        name="Wall buttons",
                        completion_worth=25,
                        completed=False,
                        state={"sequence": ["goat", "cow", "horse", None]},
                    )
                ],
            ),
            StageState(
                name="Assembling the skeleton",
                description="The players assemble a skeleton inside the coffin.",
                puzzles=[
                    PuzzleState(
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
            StageState(
                name="Picking up the book",
                description="The players collect the spellbook.",
                puzzles=[
                    PuzzleState(
                        name="Spellbook",
                        completion_worth=5,
                        completed=False,
                    )
                ],
            ),
            StageState(
                name="Spellcasting",
                description="The players cast summoning spells.",
                puzzles=[
                    PuzzleState(
                        name="Spell #1",
                        completion_worth=10,
                        completed=False,
                    ),
                    PuzzleState(
                        name="Spell #2",
                        completion_worth=10,
                        completed=False,
                    ),
                    PuzzleState(
                        name="Spell #3",
                        completion_worth=10,
                        completed=False,
                    ),
                ],
            ),
        ],
    )
