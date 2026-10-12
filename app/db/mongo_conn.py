from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="E:/expense-auto-categorizer/.env")

client = MongoClient(os.getenv("MONGO_URI"))
mongo_db = client[os.getenv("MONGO_DB")]
notes_collection = mongo_db["notes"]
