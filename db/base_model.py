# db/base_model.py

from typing import TypeVar, Type, Optional, List, Dict, Any
from bson.objectid import ObjectId
from db.connection import get_db

'''
base class for all models (auto fill everything in editor)
'''
T = TypeVar('T', bound='BaseModel')

class BaseModel:
    _collection_name: str

    def __init__(self, _id: Optional[ObjectId] = None):
        self._id = _id


    '''if you cant read, this gets the collection'''
    @classmethod
    def _get_collection(cls):
        db = get_db()
        return db[cls._collection_name]

    '''converts object to dict!!'''
    def to_dict(self) -> Dict[str, Any]:
        data = self.__dict__.copy()
        if '_collection_name' in data:
            del data['_collection_name']
        return data

    '''inserts one'''
    async def insert_one(self) -> ObjectId:
        result = await self._get_collection().insert_one(self.to_dict())
        self._id = result.inserted_id
        return self._id

    '''like find_one but lets you use a object instead of a dict'''
    @classmethod
    async def find_one(cls: Type[T], filter: Dict[str, Any]) -> Optional[T]:
        data = await cls._get_collection().find_one(filter)
        if data:
            obj = cls.from_dict(data)
            return obj
        return None

    '''similar to find_one but returns a list of objects'''
    @classmethod
    async def find_many(cls: Type[T], filter: Dict[str, Any] = {}) -> List[T]:
        cursor = cls._get_collection().find(filter)
        result = []
        async for doc in cursor:
            result.append(cls.from_dict(doc))
        return result

    '''inserts many'''
    @classmethod
    async def insert_many(cls: Type[T], objects: List[T]):
        docs = [obj.to_dict() for obj in objects]
        result = await cls._get_collection().insert_many(docs)
        for obj, inserted_id in zip(objects, result.inserted_ids):
            obj._id = inserted_id

    '''very helpful, converts the dict to an object after fetched'''
    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        obj = cls.__new__(cls)
        for key, value in data.items():
            setattr(obj, key, value)
        return obj

    '''updates a single document'''
    async def update_one(self) -> None:
        collection = self._get_collection()
        if not self._id:
            raise ValueError("cant update document without _id")

        data = self.to_dict()
        await collection.update_one(
            {"_id": self._id},
            {"$set": data}
        )

    '''deletes the document'''
    async def delete_one(self) -> None:
        if not self._id:
            raise ValueError("cant delete document without _id")
        await self._get_collection().delete_one({"_id": self._id})

