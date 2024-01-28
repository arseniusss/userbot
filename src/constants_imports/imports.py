from pymongo import MongoClient
from os import getenv
from dotenv import load_dotenv
from constants import ID_DICT
from typing import List
from telethon import TelegramClient
from telethon.sessions import StringSession


load_dotenv()
_host = getenv("MONGO_HOST")
_port = int(getenv("MONGO_PORT"))
_username = getenv("MONGO_USER")
_password = getenv("MONGO_PASSWORD")
_database = getenv("MONGO_DATABASE")
_collection = getenv("MONGO_COLLECTION")

_mongo_client = MongoClient(host=_host, port=_port)
# _mongo_client = MongoClient(host=_host, port=_port, username=_username, password=_password)
_user_db = _mongo_client[_database]
userbots_collection = _user_db[_collection]
NUMBER_OF_ACCOUNTS = len(ID_DICT.keys())
clients_array: List[TelegramClient] = []

with open('sessions.txt', 'r', encoding='utf-8') as session_file:
    for i in range(1, NUMBER_OF_ACCOUNTS+1):
        session_str = session_file.readline().replace('\n', '')
        clients_array.append(TelegramClient(StringSession(session_str), ID_DICT[f"{i}"]["api_id"], ID_DICT[f"{i}"]["api_hash"]))
        
# clients_array: List[TelegramClient] = [TelegramClient(f"{i}", ID_DICT[f"{i}"]["api_id"], ID_DICT[f"{i}"]["api_hash"]) for i in range(1, NUMBER_OF_ACCOUNTS+1)]
# with open('sessions.txt', 'w', encoding='utf-8') as file:
#     for client in clients_array:
#         data = StringSession.save(client.session)
#         file.write(data+'\n') 

print(f"{len(clients_array)} клієнтів ТГ завантажено")
RANDOMBOT_ID = 6277866886