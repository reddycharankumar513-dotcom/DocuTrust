from bson import ObjectId


def to_object_id(value: str) -> ObjectId:
    if not ObjectId.is_valid(value):
        raise ValueError("Invalid object id")
    return ObjectId(value)


def serialize_mongo(document: dict | None) -> dict | None:
    if document is None:
        return None
    serialized = dict(document)
    if "_id" in serialized:
        serialized["id"] = str(serialized.pop("_id"))
    return serialized


def serialize_many(documents: list[dict]) -> list[dict]:
    return [serialize_mongo(document) for document in documents if document is not None]
