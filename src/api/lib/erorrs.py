from fastapi import HTTPException

def NotFound(message: str):
    return HTTPException(status_code=404, detail=message)