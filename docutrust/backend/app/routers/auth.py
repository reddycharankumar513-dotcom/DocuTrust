from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.errors import DuplicateKeyError

from app.auth.dependencies import get_current_user
from app.auth.security import create_access_token, hash_password, verify_password
from app.database.mongo import get_database
from app.schemas.auth import TokenResponse, UserCreate, UserLogin, UserProfile


router = APIRouter(tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate) -> TokenResponse:
    db = get_database()
    now = datetime.now(UTC)
    user_doc = {
        "name": payload.name.strip(),
        "email": payload.email.lower(),
        "password": hash_password(payload.password),
        "created_at": now,
    }
    try:
        result = await db.users.insert_one(user_doc)
    except DuplicateKeyError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered") from exc

    user = UserProfile(id=str(result.inserted_id), name=user_doc["name"], email=user_doc["email"], created_at=now)
    return TokenResponse(access_token=create_access_token(str(result.inserted_id)), user=user)


@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin) -> TokenResponse:
    db = get_database()
    user_doc = await db.users.find_one({"email": payload.email.lower()})
    if user_doc is None or not verify_password(payload.password, user_doc["password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    profile = UserProfile(
        id=str(user_doc["_id"]),
        name=user_doc["name"],
        email=user_doc["email"],
        created_at=user_doc["created_at"],
    )
    return TokenResponse(access_token=create_access_token(str(user_doc["_id"])), user=profile)


@router.get("/profile", response_model=UserProfile)
async def profile(current_user: dict = Depends(get_current_user)) -> UserProfile:
    return UserProfile(
        id=str(current_user["_id"]),
        name=current_user["name"],
        email=current_user["email"],
        created_at=current_user["created_at"],
    )
