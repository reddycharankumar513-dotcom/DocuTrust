from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import settings


class Mongo:
    client: AsyncIOMotorClient | None = None
    db: AsyncIOMotorDatabase | None = None


mongo = Mongo()


async def connect_to_mongo() -> None:
    mongo.client = AsyncIOMotorClient(settings.mongodb_uri)
    mongo.db = mongo.client[settings.mongodb_db]
    await ensure_indexes()


async def close_mongo_connection() -> None:
    if mongo.client:
        mongo.client.close()


def get_database() -> AsyncIOMotorDatabase:
    if mongo.db is None:
        raise RuntimeError("MongoDB is not connected")
    return mongo.db


async def ensure_indexes() -> None:
    if mongo.db is None:
        return

    await mongo.db.users.create_index("email", unique=True)
    await mongo.db.documents.create_index([("user_id", 1), ("upload_time", -1)])
    await mongo.db.chat_history.create_index([("user_id", 1), ("timestamp", -1)])
    await mongo.db.interaction_logs.create_index([("user_id", 1), ("timestamp", -1)])
