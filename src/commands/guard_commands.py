from ..constants_imports.imports import clients_array, userbots_collection, NUMBER_OF_ACCOUNTS, RANDOMBOT_ID
from typing import List
from ..constants_imports.constants import WINESRA_ID
import asyncio
from collections import defaultdict


async def guard(bots_to_respond: List[int]):
    for i in bots_to_respond:
        client = clients_array[i]
        user_doc = userbots_collection.find_one(
            {
                'index': i,
            }
        )
        await client.send_message(RANDOMBOT_ID, '/rusak')
        await asyncio.sleep(0.4)
        random_messages = await client.get_messages(RANDOMBOT_ID, from_user=RANDOMBOT_ID, search="Твій русак", limit=1)
        for message in random_messages:
            if "🐒 Твій русак:"  not in message.text:
                continue
            rusak_text = message.text
            if "🎖" not in rusak_text:
                await clients_array[i].send_message(RANDOMBOT_ID, '/swap')

            chat_id = user_doc['guard_chat']
            await asyncio.sleep(0.3)
            await clients_array[i].send_message(chat_id, '/guard')


async def display_guard_chats(bots_to_respond: list, ME_ARR: list, chat_id: int, message_id: int):
    message_to_send = f"Поточні чати, в яких боти стоять на /guard:\n"
            
    async def get_chat_info(client_index: int, result_dict: dict) -> None:
        bot = userbots_collection.find_one(
                {
                    'index': client_index,
                }
            )
        chat = await clients_array[0].get_entity(bot['guard_chat'])
        result_dict[f"<a href='https://t.me/c/{str(chat.id).replace('-100', '')}'>{chat.title}</a>"].append(client_index)

    tasks = []
    status_dict = defaultdict(list)
    for i in range(NUMBER_OF_ACCOUNTS):
        task = asyncio.create_task(get_chat_info(i, status_dict))
        tasks.append(task)

    await asyncio.gather(*tasks, return_exceptions=True)
    i = 0
    for chat_link, index_arr in sorted(status_dict.items()):
        i+=1
        message_to_send += f"\n{i}. {chat_link}:"
        for index in sorted(index_arr):
            message_to_send+=f" {ME_ARR[index].first_name}({index+1});"
        message_to_send+="\n"

    await clients_array[bots_to_respond[0]].send_message(chat_id, message_to_send, reply_to=message_id, parse_mode="html")

async def add_guard_chat(bots_to_respond: List[int], ME_ARR: list, chat_id: int, message_id: int):
    botsadded = len(bots_to_respond)
    for i in bots_to_respond:
        user_doc = userbots_collection.find_one(
            {
                'index': i,
            }
        )
        if user_doc is None:
            userbots_collection.insert_one(
                {
                    'index': i,
                    'userID': ME_ARR[i].id,
                    'fullname': ME_ARR[i].first_name + ' ' + ME_ARR[i].last_name if ME_ARR[i].last_name else ME_ARR[i].first_name,
                    'chats_allowed': [chat_id],
                    'admins': [WINESRA_ID],
                    "guard_chat": chat_id,
                }
            )
        else: 
            userbots_collection.find_one_and_update(
                {
                    'index': i,
                },
                {
                    "$set": {
                        'guard_chat': chat_id,
                    }
                }
            )
    response_message = f"✅ {botsadded} бот(и/ів) успішно додали цей чат до списку /guard\nПерелік ботів: "
    for i in bots_to_respond:
        response_message+=f"{ME_ARR[i].first_name} ({i});" 
    await clients_array[bots_to_respond[0]].send_message(chat_id, response_message, reply_to=message_id)                         


async def get_guard_status(ME_ARR: list, chat_id: int, message_id: int):
    message_to_send = "Статус доступності /guard:\n"
    status_list = []
    available = 0
    async def get_guard_info(client_index: int, result_dict: dict) -> None:
        await clients_array[client_index].send_message(RANDOMBOT_ID, '/status')
        await asyncio.sleep(0.7)
        random_messages = await clients_array[client_index].get_messages(RANDOMBOT_ID, from_user=RANDOMBOT_ID, search="/daily", limit=1)
        for message in random_messages:
            result_dict[client_index] = "🟢" if "🟥 /work" in message.text else "🔴"
    tasks = []
    status_dict = defaultdict(str)
    for i in range(NUMBER_OF_ACCOUNTS):
        task = asyncio.create_task(get_guard_info(i, status_dict))
        tasks.append(task)
    
    await asyncio.gather(*tasks, return_exceptions=True)
    available = 0

    for index, status in sorted(status_dict.items()):
        message_to_send += f"\n{status} {index+1} {ME_ARR[index].first_name}"
        if status == "🟢":
            available += 1

    message_to_send += (f"\n\nУсього: {available}/{len(clients_array)}")
    await clients_array[0].send_message(chat_id, message_to_send, reply_to=message_id)