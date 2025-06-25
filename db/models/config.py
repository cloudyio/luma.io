from typing import Optional, List, Dict, Any
from bson.objectid import ObjectId
from db.base_model import BaseModel

class Config(BaseModel):
    _collection_name = "guild_configs"

    def __init__(
        self,
        _id: str,
        premium: Optional[bool] = False,
        prefix: Optional[str] = None,
    ):
        super().__init__(_id)
        self._id = str(_id)
        self.premium = premium
        self.prefix = prefix
