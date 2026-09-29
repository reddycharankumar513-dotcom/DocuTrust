from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.auth.security import decode_access_token
from app.database.mongo import get_database
from app.utils.object_id import to_object_id


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    user_id = decode_access_token(token)
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    try:
        object_id = to_object_id(user_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject") from exc

    db = get_database()
    user = await db.users.find_one({"_id": object_id})
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


async def get_user_from_token(token: str) -> dict | None:
    user_id = decode_access_token(token)
    if user_id is None:
        return None
    try:
        object_id = to_object_id(user_id)
    except ValueError:
        return None
    return await get_database().users.find_one({"_id": object_id})
