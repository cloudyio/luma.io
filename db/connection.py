
from pymongo import AsyncMongoClient

from config import MONGO_URI, DB_NAME

client: AsyncMongoClient = AsyncMongoClient(MONGO_URI)

def get_db():
    return client[DB_NAME]

async def test_connection():
    try:
        await client.admin.command('ping')
        print("MongoDB connection successful")
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
