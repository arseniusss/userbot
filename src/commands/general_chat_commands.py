import asyncio
import random
from ..constants_imports.imports import clients_array, userbots_collection, RANDOMBOT_ID
from helper_commands.emoji_handler import emoji_loot_map


async def get_curr_chat_activities(client_index: int, chat_id: int, message_id: int):
    # TODO: щоб показувало скільки часу тому була остання битва/міжчат/рейд
    chat = await clients_array[client_index].get_entity(chat_id)
    chat_link = f"<a href='https://t.me/c/{str(chat_id).replace('-100', '')}"
    message_to_send = f"Поточні активності в чаті {chat.title}:\n"
    war_msg = await clients_array[client_index].get_messages(chat, from_user=RANDOMBOT_ID, search="🌏 Починається міжчатова", limit=1)
    message_to_send+="Міжчат🌐: "
    for message in war_msg:
        if message.reply_markup is not None:
            message_to_send += f"{chat_link}/{message.id}'>тут</a>"
        else:
            message_to_send+=("зараз нема, останній був " + f"{chat_link}/{message.id}'>тут</a>")
    battle_messages = await clients_array[client_index].get_messages(chat, from_user=RANDOMBOT_ID, search="⚔️ Починається битва", limit=4)
    battle_msg = ''
    
    for message in battle_messages:
        if "Починається битва" not in message.text:
            continue
        battle_msg = f"{chat_link}/{message.id}'>тут</a>" if message.reply_markup is not None else "зараз нема, остання була " + f"{chat_link}/{message.id}'>тут</a>"
     
    if battle_msg:
        message_to_send += "\nМасова битва⚔️: " + battle_msg
    else:
        message_to_send += "\nМасова битва⚔️: не знайдено"
    
    raid_msg = await clients_array[client_index].get_messages(chat, from_user=RANDOMBOT_ID, search="💰 Починається рейд", limit=1)
    message_to_send+="\nРейд💰: "
    message_to_send+=f"{chat_link}/{raid_msg[0].id}'>тут</a>" if raid_msg[0].reply_markup is not None else f"зараз нема, останній був {chat_link}/{raid_msg[0].id}'>тут</a>"
    
    convoy_loot_msg = await clients_array[client_index].get_messages(chat, from_user=RANDOMBOT_ID, search="Русаки приїхали грабувати гумконвой", limit=1)
    message_to_send+="\nПаки з конвоя📦: "
    for message in convoy_loot_msg:
        loot_dict = emoji_loot_map(message.text)
        message_to_send += f"{chat_link}/{message.id}'>тут</a>"
        loot_str = ""
        for key, value in loot_dict.items():
            loot_str+=(str(key) + str(value))
        message_to_send+=(" ("+loot_str+")")
        if message.reply_markup is None:
            message_to_send += ", але вже зіжрали"
    
    other_loot_msg = await clients_array[client_index].get_messages(chat, from_user=RANDOMBOT_ID, search="Проведено рейд на", limit=1)
    message_to_send+="\nІнший лут🎰: "
    for message in other_loot_msg:
        loot_dict = emoji_loot_map(message.text)
        message_to_send += f"{chat_link}/{message.id}'>тут</a>"
        loot_str = ""
        for key, value in loot_dict.items():
            loot_str+=(str(key) + str(value))
        message_to_send+=(" ("+loot_str+")")
        if message.reply_markup is None:
            message_to_send += ", але вже зіжрали"
    
    await asyncio.sleep(0.5)
    await clients_array[client_index].send_message(chat_id, message_to_send, reply_to=message_id, parse_mode="html")


async def crash_battle(client_index: int, chat_id: int):
    chat = await clients_array[client_index].get_entity(chat_id)
    user_doc = userbots_collection.find_one(
        {
            "index": client_index,
        }
    )
    ids_to_delete = user_doc.get("last_battle_id", 100)
    old_battle_msg = await clients_array[client_index].get_messages(chat, ids=ids_to_delete)
    await old_battle_msg.delete()

    await asyncio.sleep(0.4+random.random()*0.6)
    await clients_array[client_index].send_message(chat_id, "/battle")
    await asyncio.sleep(0.4+random.random()*0.6)
    await clients_array[client_index].send_message(chat_id, "/battle")