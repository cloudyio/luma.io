from typing import Optional, List, Dict, Any
from bson.objectid import ObjectId
from db.base_model import BaseModel

class Command(BaseModel):
    _collection_name = "commands"

    def __init__(
        self,
        name: str,
        description: str,
        category: str,
        enabled: bool = True,
        guild_id: Optional[str] = None,
        permissions: Optional[Dict[str, Any]] = None,
        default_permissions: Optional[Dict[str, Any]] = None,
        cooldown: Optional[Dict[str, Any]] = None,
        developer_only: bool = False,
        _id: Optional[str] = None
    ):
        # create  _id from guild_id and name
        if _id is None and guild_id is not None:
            _id = f"{guild_id}:{name}"
        super().__init__(_id)
        self.name = name
        self.description = description
        self.category = category
        self.enabled = enabled
        self.guild_id = guild_id
        self.permissions = permissions or {
            "enabled_roles": [],
            "disabled_roles": [],
            "ignored_roles": [],
            "allowed_channels": [],
            "disabled_channels": []
        }
        self.default_permissions = default_permissions
        self.cooldown = cooldown or {
            "seconds": 0,
            "per_user": False
        }
        self.developer_only = developer_only

    @classmethod
    async def find_by_name_and_guild(cls, name: str, guild_id: str) -> Optional['Command']:
        return await cls.find_one({"_id": f"{guild_id}:{name}"})

    @classmethod
    async def find_by_category(cls, category: str, guild_id: Optional[str] = None) -> List['Command']:
        filter_dict = {"category": category}
        if guild_id:
            filter_dict["guild_id"] = guild_id
        return await cls.find_many(filter_dict)

    @classmethod
    async def find_enabled(cls, guild_id: Optional[str] = None) -> List['Command']:
        filter_dict = {"enabled": True}
        if guild_id:
            filter_dict["guild_id"] = guild_id
        return await cls.find_many(filter_dict)

    @classmethod
    async def find_by_guild(cls, guild_id: str) -> List['Command']:
        return await cls.find_many({"guild_id": guild_id})
