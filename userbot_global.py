from telethon import TelegramClient, events, types
from telethon.tl.functions.messages import GetBotCallbackAnswerRequest
from telethon.errors.rpcerrorlist import BotResponseTimeoutError
import asyncio
from userbot_settings import ID_DICT, mongo_client, WINESRA_ID
from pymongo import MongoClient, ASCENDING, DESCENDING
import emoji
import re
import random 
import requests
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from PIL import Image
import requests
from io import BytesIO
from typing import List
from telethon import events
from telethon.sync import events as sync_events


#initializing mongo and user collection
user_db = mongo_client['my_userbots_db']
userbots_collection = user_db['userbots_collection']

NUMBER_OF_ACCOUNTS = len(ID_DICT.keys())

clients_array: List[TelegramClient] = [TelegramClient(f"{i}", ID_DICT[f"{i}"]["api_id"], ID_DICT[f"{i}"]["api_hash"]) for i in range(1, NUMBER_OF_ACCOUNTS+1)]
print(f"{len(clients_array)} клієнтів ТГ завантажено")
COMMANDS_WITH_ONE_ANSWER_MESSAGE = ["status", "guards", "info", "chats", "stats"]
WINESRA_COMMANDS = ["addchat", "addadmin", "add_guard_chat", "guard"]
ME_ARR = []
RANDOMBOT_ID = 6277866886
BUY_OPTIONS = ["хп", "бд"] 

async def buy_something_in_shop(client_index, stuff_to_buy, quantity: int = 1):
    # TODO: додати ще щось для закупівлі
    if stuff_to_buy == "бд":
        # TODO: перевірки
        client = clients_array[client_index]
        response = await client.get_messages(RANDOMBOT_ID, from_user=RANDOMBOT_ID, search='Горілка "Козаки"', limit=1)
        if response[0].reply_markup is not None and hasattr(response[0].reply_markup, 'rows'):
            try:
                await client(GetBotCallbackAnswerRequest(
                    response[0].chat_id,
                    response[0].id,
                    data='5_vodka'
                ))
                return
            except BotResponseTimeoutError:
                pass
    elif stuff_to_buy == "хп":
        # TODO: перевірки
        client = clients_array[client_index]
        response = await client.get_messages('RandomUA3bot', from_user=RANDOMBOT_ID, search='Горілка "Козаки"', limit=1)
        if response[0].reply_markup is not None and hasattr(response[0].reply_markup, 'rows'):
            try:
                await client(GetBotCallbackAnswerRequest(
                    response[0].chat_id,
                    response[0].id,
                    data='aid_kit'
                ))
                return
            except BotResponseTimeoutError:
                pass
       

async def get_battle_message(chat, client):
    # TODO: мб видалити
    battle_messages = await client.get_messages(chat, from_user=RANDOMBOT_ID, search="⚔️ Починається битва", limit=20)
    
    for message in battle_messages:
        if "Починається битва" not in message.text:
            continue
        else:
            if message.reply_markup is not None:
                return f"<a href='https://t.me/c/{str(message.chat_id).replace('-100', '')}/{message.id}'>тут</a>"
            else:
                return "зараз нема, остання була " + f"<a href='https://t.me/c/{str(message.chat_id).replace('-100', '')}/{message.id}'>тут</a>"
    
    return None


async def get_first_bots_that_are_in_channel(client_index: int, chat_id: str, limit: int = 1) -> list:
    try:
        participants = await clients_array[client_index].get_participants(chat_id)

        user_ids = [participant.id for participant in participants]

        result_arr = []
        for id in user_ids:
            if len(result_arr) >= limit:
                return result_arr
            
            for j in range(NUMBER_OF_ACCOUNTS):
                if ME_ARR[j].id == id:
                    result_arr.append(j)
                    break

        return result_arr
    
    except Exception as e:
        return []

def emoji_loot_map(text: str) -> dict[str, int]:
    # TODO: спробувати переробити ці методи в 1
    emojis = list(emoji.emoji_list(text[text.find('\n'):]))
    emoji_list =  [e['emoji'] for e in emojis]
    map_of_emoji_loot = {}
    clan_resources = ['🌳', '🪨', '🧶', '🧱', '👾', '🪙', '🤖', '🟡']
    for my_emoji in emoji_list:
        text = text[text.find(my_emoji):]
        if not my_emoji in clan_resources:
            if my_emoji == '🍉':
                map_of_emoji_loot['🍉'] = 1
            else:
                match = re.search(r'[+-]?\d+', text)
                if match:
                    if my_emoji != '🍉':
                        map_of_emoji_loot[my_emoji] = int(match.group())
    if len(map_of_emoji_loot.keys()) == 0:
        map_of_emoji_loot = {
            'нічого корисного': ""
        }

    return map_of_emoji_loot


rusak_classes_emoji = ["🤙","🧰","🔮","🗿","🪖","👮","🤡","📟","⛑","🚬","🚕","🎖",]


def rusak_stats_map(text: str) -> dict[str, int]:
    emojis = list(emoji.emoji_list(text))
    emoji_list =  [e['emoji'] for e in emojis]
    rusak_stats = {}
    for my_emoji in emoji_list:
        text = text[text.find(my_emoji):]
        if not (my_emoji in rusak_classes_emoji) and my_emoji != "🏷" and my_emoji != '🐒':
            match = re.search(r'\d+', text)
            if match:
                rusak_stats[my_emoji] = int(match.group())

    return rusak_stats



async def filter_toggle(toggle_parameter: str, toggle_value: str, chat_id, client_index) -> str:
    user_doc = userbots_collection.find_one(
        {
            'index': client_index,
        }
    )

    if user_doc is not None:
        toggle_arr = user_doc.get(toggle_parameter, [])
        if toggle_value == "on" and chat_id not in toggle_arr:
            toggle_arr.append(chat_id)
        elif toggle_value == "off" and chat_id in toggle_arr:
            toggle_arr.remove(chat_id)
        elif toggle_value == "idk":
            return_value = "on"
            if chat_id not in toggle_arr:
                toggle_arr.append(chat_id)
            else:
                return_value = "off"
                toggle_arr.remove(chat_id)
    userbots_collection.find_one_and_update(
        {
            'index': client_index,
        },
        {
            "$set": {
                toggle_parameter: toggle_arr,
            }
        }
    )
    if toggle_value=='idk':
        return return_value


async def determine_clients_to_respond(event, client_index) -> list[int]:
    message = event.message
    if not hasattr(event.message, 'text'):
        return []
    if len(event.message.text) <= 1:
        return []
    if message.text[1:] in COMMANDS_WITH_ONE_ANSWER_MESSAGE:
        id = await get_first_bots_that_are_in_channel(client_index, event.message.chat_id)
        return list(id)
    if message.text[1].startswith('.clan') or message.text.startswith('.cl'):
        bots_to_respond = []
        for i in range(NUMBER_OF_ACCOUNTS):    
            user_doc = userbots_collection.find_one(
                {
                    'index': i,
                }
            )
            if message.chat_id == user_doc.get("guard_chat", ""):
                bots_to_respond.append(i)
        return bots_to_respond
    parts = message.text[1:].split()
    if parts:
        if '-' in parts[0]:
            range_parts = parts[0].split('-')
            if len(range_parts) == 2 and range_parts[0].isdigit() and range_parts[1].isdigit():
                start_number = int(range_parts[0])
                end_number = int(range_parts[1])
                if 1 <= start_number <= NUMBER_OF_ACCOUNTS and 1 <= end_number <= NUMBER_OF_ACCOUNTS and start_number <= end_number:
                    return list(range(start_number-1, end_number))
        if "," in parts[0]:
            num_strings = parts[0].split(",")
            numbers = [int(num.strip()) - 1 for num in num_strings]
            return numbers
        elif parts[0] == 'all':
            return list(range(NUMBER_OF_ACCOUNTS))

        elif parts[0].isdigit():
            client_number = int(parts[0])
            if 1 <= client_number <= NUMBER_OF_ACCOUNTS:
                return [client_number-1]

    return [0]


async def handle_filters(event, client_index: int):
    # TODO: п'ятихвилинна затримка перед тим, як спробувати взяти лут 
    if event.message.from_id is None:
        return

    user_doc = userbots_collection.find_one(
        {'index': client_index},
    )


    if (user_doc and event.message.chat_id not in user_doc['chats_allowed']):
        return
    message_recieved = event.message
    
    if "Додатковий гумконвой вже в дорозі!" in message_recieved.text and message_recieved.chat_id == user_doc.get('convoys_observe_chat', 0) and message_recieved.from_id.user_id == RANDOMBOT_ID:
        try:
            print(message_recieved.from_id.user_id)
            convoy_limit = user_doc.get("convoys_limit", 2)
            current_convoys = user_doc.get("number_convoys", 0)
            snatch_message_id = user_doc.get("last_raid_id", 0)
            chat_to_observe = user_doc.get("convoys_observe_chat", None)

            if current_convoys+1>=convoy_limit:                          
                try:
                    await clients_array[client_index](GetBotCallbackAnswerRequest(
                            chat_to_observe,
                            snatch_message_id,
                            data='raid_join'
                        )
                    )
                except Exception:
                    pass
                    
            userbots_collection.find_one_and_update(
                {
                    'index': client_index, 
                },
                {
                    "$inc": {
                        "number_convoys": 1,  
                    }
                },
            )
            return
        except Exception:
            pass
    
    elif "Гумконвой розграбовано" in message_recieved.text and message_recieved.chat_id == user_doc.get('convoys_observe_chat', None) and message_recieved.from_id.user_id == RANDOMBOT_ID:
        userbots_collection.find_one_and_update(
            {
                'index': client_index, 
            },
            {
                "$set": {
                    "number_convoys": 0,  
                }
            }
        )
        return
    if "Починається міжчатова битва" in message_recieved.text and message_recieved.chat_id in user_doc.get('auto_war', []) :
        try:
            await buy_something_in_shop(client_index, "бд")
            await clients_array[client_index].send_message(message_recieved.chat_id, "Я купив горілку")
            if message_recieved.reply_markup is not None and hasattr(message_recieved.reply_markup, 'rows'):
                for row in message_recieved.reply_markup.rows:
                    for button in row.buttons:
                        if "міжчатовий бій" in button.text:                       
                            await asyncio.sleep(0.2+random.random()*0.2)
                            await clients_array[client_index](GetBotCallbackAnswerRequest(
                                message_recieved.chat_id,
                                message_recieved.id,
                                data=button.data
                            ))
                            return
        except Exception as e:
            pass
    
    if "Починається битва" in message_recieved.text and message_recieved.chat_id in user_doc.get('auto_battle', []):
        try:
            if message_recieved.reply_markup is not None and hasattr(message_recieved.reply_markup, 'rows'):
                user_doc = userbots_collection.find_one(
                    {
                        'index': client_index,
                    }
                )
                sleep = user_doc.get("battle_sleep", 0.7+0.2*client_index+random.random()*1)
                userbots_collection.find_one_and_update(
                    {
                        "index": client_index,
                    },
                    {
                        "$set": {
                            "last_battle_id": message_recieved.id,
                        }
                    }
                )
                
                await asyncio.sleep(sleep + random.random()*0.4)
                await clients_array[client_index](GetBotCallbackAnswerRequest(
                    message_recieved.chat_id,
                    message_recieved.id,
                    data='join'
                ))
                return
        except Exception as e:
            pass
    
    if "Починається рейд" in message_recieved.text and message_recieved.from_id.user_id == RANDOMBOT_ID:
        try:
            if message_recieved.chat_id == user_doc.get("convoys_observe_chat", -1001973237747):
                userbots_collection.find_one_and_update(
                {
                    "index": client_index,
                },
                {
                    "$set": {
                        "last_raid_id": message_recieved.id,
                        }
                    }
                )
            if message_recieved.chat_id in user_doc.get('auto_raid', []) and message_recieved.reply_markup is not None and hasattr(message_recieved.reply_markup, 'rows'):
                for row in message_recieved.reply_markup.rows:
                    for button in row.buttons:
                        if "на рейд" in button.text:                          
                            await asyncio.sleep(0.2+random.random()*0.2)
                            await clients_array[client_index](GetBotCallbackAnswerRequest(
                                message_recieved.chat_id,
                                message_recieved.id,
                                data='raid_join'
                            ))
                            return
        except Exception as e:
            pass    
    if "Міжчатова битва русаків завершена!" in message_recieved.text and message_recieved.chat_id in user_doc.get('auto_start_war', []):
        await clients_array[client_index].send_message(message_recieved.chat_id, '/war')
        return
    if ("/battle" in message_recieved.text or "завершена" in message_recieved.text)  and message_recieved.chat_id in user_doc.get("auto_start_battle", []) and message_recieved.text!="/battle":
        await clients_array[client_index].send_message(message_recieved.chat_id, '/battle')
        return
    if "Проведено рейд" in message_recieved.text or "Русаки приїхали грабувати" in message_recieved.text:
        if message_recieved.chat_id in user_doc.get("auto_start_raid", []):
            if "наступний рейд" in message_recieved.text or "реванш" in message_recieved.text:
                await clients_array[client_index].send_message(message_recieved.chat_id, '/raid')
            else:
                await clients_array[client_index].send_message(message_recieved.chat_id, '/raid', schedule=timedelta(seconds=3600 + random.randint(10, 20)))
        if message_recieved.chat_id in user_doc.get("auto_loot", []):
            print(client_index)
            if message_recieved.reply_markup is not None and hasattr(message_recieved.reply_markup, 'rows'):
                for row in message_recieved.reply_markup.rows:
                    for button in row.buttons:
                        try:
                            await clients_array[client_index](GetBotCallbackAnswerRequest(
                                message_recieved.chat_id,
                                message_recieved.id,
                                data=button.data
                            ))
                            await asyncio.sleep(0.05)
                        except Exception as e:
                            pass
                await clients_array[client_index].send_message(message_recieved.chat_id, '+', reply_to=message_recieved.id) 
                if any(item in message_recieved.text for item in ['🍝', '🍛', '🍜', '🥗', '🌭']):
                    await clients_array[client_index].send_message(event.message.chat_id, '/feed')

async def message_handler(event, client_index: int):
    global COMMANDS_WITH_ONE_ANSWER_MESSAGE, ME_ARR, WINESRA_ID
    message_recieved = event.message
    await handle_filters(event, client_index)

    if not (message_recieved.text.startswith('.')):
        return
    
    user_doc = userbots_collection.find_one(
        {
            'index': client_index,
        }
    )

    sender = await event.get_sender()
    sender_id = sender.id

    if not (sender_id == WINESRA_ID or sender_id == ME_ARR[client_index].id or sender_id in user_doc.get("admins", [])):
        return
    
    if (user_doc and message_recieved.chat_id not in user_doc['chats_allowed'] and sender_id != WINESRA_ID):
        return
    
    bots_to_respond = await determine_clients_to_respond(event, client_index)
    if client_index not in bots_to_respond:
        return
        
    message_args = message_recieved.text.split()
    if len(message_recieved.text.split()) >=2:
        if client_index!=bots_to_respond[0] and client_index!=0:
            return
        if str(message_args[1]).startswith("/"):
            if message_args[1] == "/openpack":
                await clients_array[bots_to_respond[0]].send_message(message_recieved.chat_id, f"іДі нахуй, я жадібний", reply_to=message_recieved.id)
                return
            for i in bots_to_respond:
                await clients_array[i].send_message(message_recieved.chat_id, message_args[1])
        if message_args[1] in BUY_OPTIONS:
            tasks = []
            for i in bots_to_respond:
                tasks.append(buy_something_in_shop(i, message_args[1]))
            await asyncio.gather(*tasks)
            await clients_array[bots_to_respond[0]].send_message(message_recieved.chat_id, f"Я купив {message_args[1]} на {len(bots_to_respond)} аккаунтах", reply_to=message_recieved.id)
        
        if message_args[1] in ["rusak", "русак", "r", 'р']: 
            # TODO: параметр -2 для другого русака/другого класу
            message_to_send = "📊Стати обраних русаків:\n"

            async def get_acc_info(client_index: int, classes_dict: str) -> dict[str, int]:
                await clients_array[client_index].send_message(RANDOMBOT_ID, '/rusak')
                classes_dict[client_index] = '✖️'
                await asyncio.sleep(0.5)
                random_messages = await clients_array[client_index].get_messages(RANDOMBOT_ID, from_user=RANDOMBOT_ID, search="Твій русак", limit=1)
                for message in random_messages:
                    index_of_class = message.text.find(" Клас:")
                    if index_of_class != -1:
                        lines = message.text.split('\n')
                        classes_dict[client_index] = lines[7][:str(lines[7]).find(" ")]
                    stats = rusak_stats_map(message.text)
                    return stats
                
            tasks = []
            indices = []
            classes_dict = defaultdict(list)
            for i in bots_to_respond:
                task = asyncio.create_task(get_acc_info(i, classes_dict))
                tasks.append(task)
                indices.append(i)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            sorted_results = sorted(zip(indices, results), key=lambda x: indices.index(x[0]))

            for i, _dict in sorted_results:
                message_to_send+=f"\n{classes_dict[i]}{ME_ARR[i].first_name}({i+1}):"
                for key, value in _dict.items():
                    message_to_send+=f" {(key)}{value}"
                message_to_send+=";"
            
            await clients_array[bots_to_respond[0]].send_message(message_recieved.chat_id, message_to_send, reply_to=message_recieved.id)

        if message_args[1] in ["account", "акк", 'acc', 'а', 'a']:
            message_to_send = "💵📦🧂🌀🌟Стати акаунтів русаків:\n"
            total_dict = {}
            async def get_acc_info(client_index: int) -> dict[str, int]:
                await clients_array[client_index].send_message(RANDOMBOT_ID, '/account')
                await asyncio.sleep(0.4)
                random_messages = await clients_array[client_index].get_messages(RANDOMBOT_ID, from_user=RANDOMBOT_ID, search="💵 Гривні:", limit=1)
                for message in random_messages:
                    stats = rusak_stats_map(message.text)
                    return stats
                
            tasks = []
            indices = []
            for i in bots_to_respond:
                task = asyncio.create_task(get_acc_info(i))
                tasks.append(task)
                indices.append(i)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            sorted_results = sorted(zip(indices, results), key=lambda x: indices.index(x[0]))

            for i, _dict in sorted_results:
                if i == bots_to_respond[0]:
                    total_dict = _dict.copy()
                message_to_send+=f"\n{ME_ARR[i].first_name}({i+1}):"
                for key, value in _dict.items():
                    message_to_send+=f" {(key)}{value}"
                    if i!= bots_to_respond[0]:
                        total_dict[key] += value
                message_to_send+=";"
            
            message_to_send+="\n\nУсього:"
            for key, value in total_dict.items():
                message_to_send+=f" {(key)}{value}"
            message_to_send+=";"
            await clients_array[bots_to_respond[0]].send_message(message_recieved.chat_id, message_to_send, reply_to=message_recieved.id)

        elif message_args[1] == "observe_convoys":
            for i in bots_to_respond:
                user_doc = userbots_collection.find_one(
                    {
                        'index': i,
                    }
                )
                if user_doc is not None:
                    userbots_collection.find_one_and_update(
                        {
                            'index': i,
                        },
                        {
                            "$set": {
                                'convoys_observe_chat': event.chat_id,
                            }   
                        }
                    )
        elif message_args[1] == "addchat":
            # TODO: все те саме, тільки з remove
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
                            'chats_allowed': [message_recieved.chat_id],
                            'admins': [WINESRA_ID],
                        }
                    )
                else: 
                    current_chats_allowed = user_doc['chats_allowed']
                    if message_recieved.chat_id not in current_chats_allowed:
                        current_chats_allowed.append(message_recieved.chat_id)
                    userbots_collection.find_one_and_update(
                        {
                            'index': i,
                        },
                        {
                            "$set": {
                                'chats_allowed': current_chats_allowed
                            }
                        }
                    )
            await clients_array[bots_to_respond[0]].send_message(message_recieved.chat_id, f"✅ {botsadded} бот(и/ів) успішно додали чат {message_recieved.chat_id} до списку чатів", reply_to=message_recieved.id)                          

        elif message_args[1] == "addadmin":
            reply_to_user = None
            botsadded = len(bots_to_respond)
            for i in bots_to_respond:
                user_doc = userbots_collection.find_one(
                    {
                        'userID': ME_ARR[i].id,
                    }
                )
                if user_doc is None:
                    userbots_collection.insert_one(
                        {
                            'index': i,
                            'userID': ME_ARR[i].id,
                            'fullname': ME_ARR[i].first_name + ' ' + ME_ARR[i].last_name if ME_ARR[i].last_name else ME_ARR[i].first_name,
                            'chats_allowed': [message_recieved.chat_id],
                            'admins': [WINESRA_ID],
                        }
                    )
                else: 
                    current_admins = user_doc['admins']
                    original_message = await message_recieved.get_reply_message()
                    reply_to_user = await clients_array[0].get_entity(original_message.from_id.user_id)
                    if reply_to_user.id not in current_admins:
                        current_admins.append(reply_to_user.id)
                    userbots_collection.find_one_and_update(
                        {
                            'index': i,
                        },
                        {
                            "$set": {
                                'admins': current_admins
                            }
                        }
                    )
                    
            await clients_array[bots_to_respond[0]].send_message(message_recieved.chat_id, f"✅ {botsadded} бот(и/ів) успішно додали користувача {reply_to_user.first_name} до списку адмінів", reply_to=message_recieved.id)                          
        
        elif message_args[1] == "add_guard_chat":
            botsadded = len(bots_to_respond)
            for i in bots_to_respond:
                user_doc = userbots_collection.find_one(
                    {
                        'userID': ME_ARR[i].id,
                    }
                )
                if user_doc is None:
                    userbots_collection.insert_one(
                        {
                            'index': i,
                            'userID': ME_ARR[i].id,
                            'fullname': ME_ARR[i].first_name + ' ' + ME_ARR[i].last_name if ME_ARR[i].last_name else ME_ARR[i].first_name,
                            'chats_allowed': [message_recieved.chat_id],
                            'admins': [WINESRA_ID],
                            "guard_chat": event.message.chat_id,
                        }
                    )
                else: 
                    userbots_collection.find_one_and_update(
                        {
                            'index': i,
                        },
                        {
                            "$set": {
                                'guard_chat': event.message.chat_id,
                            }
                        }
                    )
            response_message = f"✅ {botsadded} бот(и/ів) успішно додали цей чат до списку /guard\nПерелік ботів: "
            for i in bots_to_respond:
                response_message+=f"{ME_ARR[i].first_name} ({i});" 
            await clients_array[bots_to_respond[0]].send_message(event.message.chat_id, response_message, reply_to=message_recieved.id)   
        
        elif message_args[1] == "guard":
            # TODO: потім додати багатопоточність
            for i in bots_to_respond:
                client = clients_array[i]
                user_doc = userbots_collection.find_one(
                    {
                        'userID': ME_ARR[i].id,
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
        
        elif message_args[1] == "class":
            # TODO: багатопоточність
            response_message = f"Класи русаків - поточний (додатковий):\n"
            for i in bots_to_respond:
                emoji_primary, emoji_secondary = "✖️", "✖️"
                user_doc = userbots_collection.find_one(
                    {
                        'userID': ME_ARR[i].id,
                    }
                )
                await clients_array[i].send_message(RANDOMBOT_ID, '/rusak')
                await asyncio.sleep(0.4)
                random_messages = await clients_array[i].get_messages(RANDOMBOT_ID, from_user=RANDOMBOT_ID, search="Твій русак", limit=1)
                for message in random_messages:
                    if "🐒 Твій русак:" not in message.text:
                        continue
                    index_of_class = message.text.find(" Клас:")
                    if index_of_class != -1:
                        lines = message.text.split('\n')
                        emoji_primary = lines[7][:str(lines[7]).find(" ")]
                
                await clients_array[i].send_message(RANDOMBOT_ID, '/swap')
                await clients_array[i].send_message(RANDOMBOT_ID, '/rusak')
                await asyncio.sleep(0.5+random.random()*0.3)
                random_messages2 = await clients_array[i].get_messages(RANDOMBOT_ID, from_user=RANDOMBOT_ID, search="Твій русак", limit=1)
                for message in random_messages2:
                    if "🐒 Твій русак:" not in message.text:
                        continue
                    index_of_class = message.text.find(" Клас:")
                    if index_of_class != -1:
                        lines = message.text.split('\n')
                        emoji_secondary = lines[7][:str(lines[7]).find(" ")]
                
                await clients_array[i].send_message(RANDOMBOT_ID, '/swap')
                await asyncio.sleep(0.3)
                response_message += f"{ME_ARR[i].first_name}({i+1}): {emoji_primary}({emoji_secondary});\n"
            
            await asyncio.sleep(0.5)
            await clients_array[bots_to_respond[0]].send_message(event.message.chat_id, response_message)
        
        elif message_args[1] in ["war", "battle", "loot", "start_war", "start_battle", "raid", "start_raid", "battle_sleep", "count_convoys", "makima_mode", "convoys_limit"]:
            "🌐⚔️🎰"
            single_bot = len(bots_to_respond)==1

            def get_toggle_responses(key: str, single_bot:bool = False) -> str:
                toggle_responses = {
                    "war": f"заходитим{'е' if single_bot else 'уть'} в міжчатові битви автоматично🌐",
                    "start_war": f"починатим{'е' if single_bot else 'уть'} міжчатові битви автоматично🌐(🔄)",
                    "battle": f"заходитим{'е' if single_bot else 'уть'} в масові битви автоматично⚔️",
                    "start_battle": f"починатим{'е' if single_bot else 'уть'} міжчатові битви автоматично⚔️(🔄)",
                    "raid": f"заходитим{'е' if single_bot else 'уть'} в рейди автоматично💰",
                    "start_raid": f"починатим{'е' if single_bot else 'уть'} рейди автоматично💰(🔄)",
                    "makima_mode": f"пиздитим{'е' if single_bot else 'уть'} конвої автоматично🚛",
                    "loot": f"пиздитим{'e' if single_bot else 'уть'} лут автоматично",
                }

                return toggle_responses[key]

            response_message = f"Фільтри змінено: бот {'#' if len(bots_to_respond) == 1 else 'и'}"

            if message_args[1] == "battle_sleep":
                for i in bots_to_respond:
                    user_doc = userbots_collection.find_one(
                        {
                            'index': i,
                        }
                    )
                    if user_doc is not None:
                        userbots_collection.find_one_and_update(
                            {
                                'index': i,
                            },
                            {
                                "$set": {
                                    "battle_sleep": float(message_args[2]),
                                }
                            }
                        )
                response_message+=f"{', '.join(map(str, [bot+1 for bot in bots_to_respond]))} чекатим{'е' if single_bot else 'уть'} {float(message_args[2])}⏳ секунд(и) перед тим, як заходити в масову битву в цьому чаті."
                
            
            elif message_args[1] == 'convoys_limit':
                for i in bots_to_respond:
                    userbots_collection.find_one_and_update(
                        {
                            'index': i,
                        },
                        {
                            "$set": {
                                "convoys_limit": int(message_args[2]),
                            }
                        }
                    )
                response_message+=f"{', '.join(map(str, [bot+1 for bot in bots_to_respond]))} автоматично заходитим{'е' if single_bot else 'уть'} в рейд після того, як буде покликано {int(message_args[2])} гумконво{'й' if int(message_args[2]) == 1 else 'я'}🚛."

            else:
                toggle_parameter = message_args[1]
                toggle_value = "idk" if len(message_args) == 2 else message_args[2]
                if toggle_value!="idk":
                    response_message+=f"{', '.join(map(str, [bot+1 for bot in bots_to_respond]))} тепер {'НЕ ' if toggle_value=='off' else ''}{get_toggle_responses(toggle_parameter, len(bots_to_respond)==1)}"
                else:
                    response_message = f"Фільтри змінено:"
                toggled_dict = defaultdict(list)
                for i in bots_to_respond:
                    toggle_result = await filter_toggle("auto_" + toggle_parameter, toggle_value, event.message.chat_id, i)
                    if toggle_value == "idk":
                        toggled_dict[toggle_result].append(i)

                for key, value in toggled_dict.items():
                    if len(value):
                        response_message+=f"\nбот{'и ' if len(value)!=1 else f'#'}{','.join(map(str, [v+1 for v in value]))} тепер {'НЕ ' if key=='off' else ''}{get_toggle_responses(toggle_parameter, len(value)==1)};" 
            
            await clients_array[bots_to_respond[0]].send_message(event.message.chat_id, response_message, reply_to=event.message.id)
        
        elif message_args[1] == "filters":
            #TODO: якийсь нормальний /i
            #TODO: admins
            # TODO: норм оформлення, щоб автоматично викликалось тільки для .cl
            title_chat = await clients_array[0].get_entity(event.message.chat_id)
            title_chat = title_chat.title
            response_message = f"Увімкнені фільтри чату {title_chat}:\n\n"
            for i in bots_to_respond:
                user_doc = userbots_collection.find_one(
                    {
                        'index': i,
                    }
                )
                response_message+=f"{ME_ARR[i].first_name}({i+1}): "
                response_message+="🌐" if event.message.chat_id in user_doc.get("auto_war", []) else ""
                response_message+="(🔄)" if event.message.chat_id in user_doc.get("auto_start_war", []) else ""
                response_message+="⚔️" if event.message.chat_id in user_doc.get("auto_battle", []) else ""
                response_message+="(🔄)" if event.message.chat_id in user_doc.get("auto_start_battle", []) else ""
                response_message+="💰" if event.message.chat_id in user_doc.get("auto_raid", []) else ""
                response_message+="(🔄)" if event.message.chat_id in user_doc.get("auto_start_raid", []) else ""
                response_message+="🎰" if event.message.chat_id in user_doc.get("auto_loot", []) else ""
                response_message+="🚛" if event.message.chat_id in user_doc.get("auto_makima_mode", []) else ""
                response_message+=f"({user_doc.get('convoys_limit', 2)})" if event.message.chat_id in user_doc.get("auto_makima_mode", []) else ""
                response_message+="\n"
            
            await clients_array[bots_to_respond[0]].send_message(event.message.chat_id, response_message)
        
        elif message_args[1] in ["клік", "тиць", ".", "👉", "☝️", "👆"]:
            # TODO: розширити заборонені слова
            # TODO: багатопоточність сюди
            # TODO: дуелі, турніри
            # TODO: refresh - видалення поточного міжчату, два рази надіслати вар, те ж саме з битвами
            BANNED_CLICK_WORDS = {
                "в жертву": "Не буду я його різати, мені жаль",
                "Атакувати": "На це буде окрема команда, поки не можу",
                "Купити": "В нас і так ресурсів забагато",
                "Продати": "Лідер/заступ буде - розбереться",
                "Викинути": "Нічого не викидаю, мені все треба",
                "Так": "Паки відкриває мій хазяїн",
                "Совєцкій пайок": "Не треба, ще шизи надає",
                "🟢": "Хуйня баф, воно нам не треба",
                "🟠": "Які рейди на клани? Ми в лізі...",
                "🔴": "Тут хуй п'ять разів на день збираються, раз на 45 хв - то забагато",
                "Перерозподіл": "З паків гроші налутаєш",
                "БПЛА": "Щоб що мені БПЛА?",
                "🟣": "Потім подивлюсь",
                "Змінити квести": "Якби в мене був мозок, щоб знати, чи хороші це квести, я б може й змінив",
            }
            
            row_index = int(message_args[2]) if len(message_args) >=3 else 1
            col_index = int(message_args[3]) if len(message_args) >=4 else 1
            
            original_message = await message_recieved.get_reply_message()
            if original_message.reply_markup is not None and hasattr(original_message.reply_markup, 'rows'):
                for i in bots_to_respond:
                    for i_row, row in enumerate(original_message.reply_markup.rows, start=1):
                        if i_row != row_index:
                            continue
                        for j_col, button in enumerate(row.buttons, start=1):
                            if j_col != col_index:
                                continue
                            for key, val in BANNED_CLICK_WORDS.items():
                                if key in button.text:
                                    await clients_array[i].send_message(message_recieved.chat_id, val, reply_to=message_recieved.id)
                                    return
                            try:
                                await clients_array[i](GetBotCallbackAnswerRequest(
                                    original_message.chat_id,
                                    original_message.id,
                                    data=button.data
                                ))
                                await asyncio.sleep(0.05)
                            except Exception as e:
                                pass
        elif message_args[1] in ["set_raid", "set_r", 'r']:
            if client_index != bots_to_respond[0]:
                return
            for i in bots_to_respond:
                user_doc=userbots_collection.find_one(
                    {
                    'index':i,
                    }
                )

    else:
        user_ids = await get_first_bots_that_are_in_channel(client_index, event.message.chat_id)
        if message_recieved.text == ".status":
            status_list = [f"{'🟢' if clients_array[i].is_connected() else '🔴'} {ME_ARR[i].first_name + ' ' + ME_ARR[i].last_name if ME_ARR[i].last_name else ME_ARR[i].first_name}" for i in range(NUMBER_OF_ACCOUNTS)]
            status_message = "Увімкнені боти:\n\n" + "\n".join(status_list)
            await clients_array[user_ids[0]].send_message(event.message.chat_id, status_message)
            return
        
        if message_recieved.text == ".тривога":
            response = requests.get("http://alerts.com.ua/map.png")
            
            image = Image.open(BytesIO(response.content))
            
            png_image_path = "image.png"
            image.save(png_image_path, "PNG")
            
            # Send the PNG image
            await clients_array[0].send_file(
                event.message.chat_id,
                png_image_path,
                background=False,
            )

        elif message_recieved.text == ".guards":
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
            await clients_array[0].send_message(event.message.chat_id, message_to_send, reply_to=event.message.id)
        
        elif message_recieved.text == '.chats':
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

            await clients_array[bots_to_respond[0]].send_message(event.message.chat_id, message_to_send, reply_to=event.message.id, parse_mode="html")

        elif message_recieved.text == ".info":
            # TODO: щоб показувало скільки часу тому була остання битва/міжчат/рейд
            chat = await clients_array[bots_to_respond[0]].get_entity(event.message.chat_id)
            message_to_send = f"Поточні активності в чаті {chat.title}:\n"
            war_msg = await clients_array[bots_to_respond[0]].get_messages(chat, from_user=RANDOMBOT_ID, search="🌏 Починається міжчатова", limit=1)
            message_to_send+="Міжчат🌐: "
            for message in war_msg:
                if message.reply_markup is not None:
                    message_to_send += f"<a href='https://t.me/c/{str(message.chat_id).replace('-100', '')}/{message.id}'>тут</a>"
                else:
                    message_to_send+=("зараз нема, останній був " + f"<a href='https://t.me/c/{str(message.chat_id).replace('-100', '')}/{message.id}'>тут</a>")

            battle_msg = await get_battle_message(chat, clients_array[bots_to_respond[0]])

            if battle_msg:
                message_to_send += "\nМасова битва⚔️: " + battle_msg
            else:
                message_to_send += "\nМасова битва⚔️: не знайдено"
            
            raid_msg = await clients_array[bots_to_respond[0]].get_messages(chat, from_user=RANDOMBOT_ID, search="💰 Починається рейд", limit=1)
            message_to_send+="\nРейд💰: "
            for message in raid_msg:
                if message.reply_markup is not None:
                    message_to_send += f"<a href='https://t.me/c/{str(message.chat_id).replace('-100', '')}/{message.id}'>тут</a>"
                else:
                    message_to_send+=("зараз нема, останній був " + f"<a href='https://t.me/c/{str(message.chat_id).replace('-100', '')}/{message.id}'>тут</a>")
            
            convoy_loot_msg = await clients_array[bots_to_respond[0]].get_messages(chat, from_user=RANDOMBOT_ID, search="Русаки приїхали грабувати гумконвой", limit=1)
            message_to_send+="\nПаки з конвоя📦: "
            for message in convoy_loot_msg:
                loot_dict = emoji_loot_map(message.text)
                message_to_send += f"<a href='https://t.me/c/{str(message.chat_id).replace('-100', '')}/{message.id}'>тут</a>"
                loot_str = ""
                for key, value in loot_dict.items():
                    loot_str+=(str(key) + str(value))
                message_to_send+=(" ("+loot_str+")")
                if message.reply_markup is None:
                    message_to_send += ", але вже зіжрали"
            
            other_loot_msg = await clients_array[bots_to_respond[0]].get_messages(chat, from_user=RANDOMBOT_ID, search="Проведено рейд на", limit=1)
            message_to_send+="\nІнший лут🎰: "
            for message in other_loot_msg:
                loot_dict = emoji_loot_map(message.text)
                message_to_send += f"<a href='https://t.me/c/{str(message.chat_id).replace('-100', '')}/{message.id}'>тут</a>"
                loot_str = ""
                for key, value in loot_dict.items():
                    loot_str+=(str(key) + str(value))
                message_to_send+=(" ("+loot_str+")")
                if message.reply_markup is None:
                    message_to_send += ", але вже зіжрали"
            
            await asyncio.sleep(0.5)
            await clients_array[bots_to_respond[0]].send_message(event.message.chat_id, message_to_send, parse_mode="html")

        elif message_recieved.text == ".crash":
            if client_index!=bots_to_respond[0]:
                return
            chat = await clients_array[bots_to_respond[0]].get_entity(event.message.chat_id)
            user_doc = userbots_collection.find_one(
                {
                    "index": client_index,
                }
            )
            ids_to_delete = user_doc.get("last_battle_id", 100)
            old_battle_msg = await clients_array[bots_to_respond[0]].get_messages(chat, ids=ids_to_delete)
            await old_battle_msg.delete()

            await asyncio.sleep(0.4+random.random()*0.6)
            await clients_array[bots_to_respond[0]].send_message(event.message.chat_id, "/battle")
            await asyncio.sleep(0.4+random.random()*0.6)
            await clients_array[bots_to_respond[0]].send_message(event.message.chat_id, "/battle")
        elif message_recieved.text in [".raid", '.r']:
            if client_index != user_ids[0]:
                return
            user_doc = userbots_collection.find_one(
                {
                    'index': client_index,
                }
            )
            last_raid = user_doc.get('last_raid_id', None)
            await clients_array[user_ids[0]].send_message(event.message.chat_id, "Останній рейд був тут", reply_to=last_raid)
        elif message_recieved.text in [".help", ".h", "хелп", "допомога", "домопожіть"]:
            message_to_send = '''**Меню команд**
            \n🌐Команди, які не потребують зазначення індекса бота🌐:
            •`.status` - список ботів з назвами та індексами, увімкнені позначені зеленим;
            •`.chats` - список чатів, звідки боти кличуть гумконвої;
            •`.guards` - статус доступності гумконвоїв (зелене - доступний);
            •`.info` - поточні активності чату з посиланнями;
            •`.тривога` - тривога (кривий код, фіксити не хочу);
            •`.raid` - останній рейд цього чату;
            \n**👉Як звернутись до ботів?👈**
            Усі команди починаються з префікса - . Після цього можна зазначити:
            •одне число (приклад .1 команда) - єдиний бот;
            •два числа через - тире (приклад: .2-6) - всі з проміжку від 1-го до 2-го числа;
            •числа,через,кому (приклад: .1,4,9) - всі перелічені боти;
            •.cl (приклад: .cl хп) - всі боти клану;         
            •.all (приклад: .all бд) - всі боти одразу;
            \n📋**Перелік команд📋**
            •клік/тиць/. (приклад: .1 клік) - тикнути на кнопку. Приклад: `.2 клік 3 4` - клікне на 4-ту кнопку 3-го ряду. 3 і 4 - небов'язкові аргументи. Якщо не вказати 3, шукатиме 1 кнопку в 1 ряді, якщо не вказати 4 - шукатиме 1 кнопку в 3 ряді;
            •rusak/русак/r (приклад: .all r) - обрані русаки та їх стати;
            •account/acc/a (приклад: .all a) - аккаунти русаків;
            •class (приклад: .1-3 class) - класи всіх русаків;
            •бд (приклад: .1 бд) - закупити бойовий дух (5 пляшок горілки);
            •хп (приклад: .cl хп) - закупити хп (одна аптечка);
            •guard (приклад: .9-10 guard) - покликати гумконвой. Само перевірить, чи обраний генерал;
            •/інші_команди (команди рандомбота) можна відправити одразу після /. Приклад: (.1 /i);
            \n🔍**Фільтри🔍**
            Щоб змінити фільтр, треба надіслати: .1 (назва фільтра) on/off/нічого. Якщо нічого не вказати, то зміниться з true на false і навпаки.
            •war - автозахід в міжчати;
            •start_war - автоматичний старт міжчатів;
            •battle - автозахід в битви;
            •start_battle - автоматичний старт масових битв;
            •raid - автозахід в рейд;
            •start_raid - автоматичний старт рейдів;
            •loot - автоматична крадіжка луту(має поставити + після крадіжки);
            •battle_sleep - затримка перед тим, як зайти в битву (приклад: .3 battle_sleep 0.5);
            •makima_mode - дозволити боту автоматично заходити в рейд після того, як пустять гумконвой (приклад: .1 makima_mode on);
            •convoys_limit - після якого числа пущених конвоїв бот зайде в рейд (приклад: .1 convoys_limit 2);
            '''
            await clients_array[bots_to_respond[0]].send_message(event.message.chat_id, message_to_send, reply_to=event.message.id, parse_mode="md")

        elif message_recieved.text in ["конвой", "камвой", ".convoy"]:
            user_doc = userbots_collection.find_one(
                {
                    'index': user_ids[0],
                }
            )
            chat_to_observe = user_doc.get("convoys_observe_chat", None)
            number_convoys = user_doc.get("number_convoys", 0)
            convoy_looted_msd = await clients_array[user_ids[0]].get_messages(chat_to_observe, search='Гумконвой розграбовано', from_user=RANDOMBOT_ID)
            for msg in convoy_looted_msd:
                id = msg.id
            
            await clients_array[0].send_message(event.message.chat_id, f"Я нарахував {number_convoys} конвоїв, розграбували тут.", reply_to=id)   

            

async def delete_old_messages():
    try:
        chat = await clients_array[0].get_entity(-1002094155156)
        for i in range(NUMBER_OF_ACCOUNTS):
            user_doc = userbots_collection.find_one(
                {
                    "index": i,
                }
            )
            if -1002094155156 in user_doc.get("auto_battle", []):
                break
        ids_to_delete = user_doc.get("last_battle_id", 100)
        old_battle_msgs = await clients_array[0].get_messages(chat, ids=ids_to_delete)

        old_date_utc = old_battle_msgs.date + timedelta(hours=2, seconds=60)

        formatted_old_date = old_date_utc.strftime('%Y-%m-%d %H:%M:%S.%f')

        formatted_current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        # FIXME: hours=2
        if formatted_old_date < formatted_current_date:
            await old_battle_msgs.delete()
            await clients_array[0].send_message(-1002094155156, "Знову видаляти, дайте поспати...")
            await asyncio.sleep(0.4+random.random()*0.6)
            await clients_array[0].send_message(-1002094155156, "/battle")
            await asyncio.sleep(0.4+random.random()*0.6)
            await clients_array[0].send_message(-1002094155156, "/battle")

    except Exception as e:
        pass

async def count_convoys_and_start_raid():
    for i in range(NUMBER_OF_ACCOUNTS):
        user_doc = userbots_collection.find_one(
            {
                'index': i,
            }
        )
        if user_doc is not None:
            chats_to_count_convoys_in = user_doc.get("auto_count_convoys", [])
            chat_to_observe = user_doc.get("convoys_observe_chat", None)
            if chat_to_observe is not None:
                convoy_looted_msd = await clients_array[i].get_messages(chat_to_observe, search='Гумконвой розграбовано', from_user=RANDOMBOT_ID)
                for msg in convoy_looted_msd:
                    convoy_id = msg.id
                
                add_convoy_msgs = await clients_array[i].get_messages(chat_to_observe, search='Додатковий гумконвой', from_user=RANDOMBOT_ID, min_id=convoy_id)
                
                userbots_collection.find_one_and_update(
                    {
                        'index': i,
                    },
                    {
                        "$set": {
                            "number_convoys": len(add_convoy_msgs),
                        }
                    }
                )
                # await clients_array[i].send_message(chat_to_observe, f"Я нарахував {len(add_convoy_msgs)} конвоїв, розграбували тут.", reply_to=convoy_id)

                
                last_raid_id = user_doc.get("last_raid_id", 0)
                raid_msgs = await clients_array[i].get_messages(chat_to_observe, search='Починається рейд...', from_user=RANDOMBOT_ID, min_id=last_raid_id)
                
                if len(raid_msgs) !=0:
                    for mesg in raid_msgs:
                        last_raid_id = max(mesg.id, last_raid_id)
                
                    await asyncio.sleep(1)
                    userbots_collection.find_one_and_update(
                        {
                            "index": i,
                        },
                        {
                            "$set": {
                                "last_raid_id": last_raid_id,
                                }
                            }
                        )
                
                #await clients_array[i].send_message(chat_to_observe, f"Останній рейд був тут", reply_to=last_raid_id)
            
        #FIXME: якусь перевірку того, чи не висить рейд вже, і мб видалити попередній
        start_raid_arr = user_doc.get('auto_start_raid', [])
        print(i, start_raid_arr)
        if start_raid_arr:
            for idx in start_raid_arr:
                await clients_array[i].send_message(idx, '/raid')
                
    pass
async def background_task():
    while True:
        await delete_old_messages()
        await asyncio.sleep(60)

async def start_clients():
    global ME_ARR
    tasks = []
    for i, client in enumerate(clients_array):
        client.add_event_handler(lambda e, index=i: message_handler(e, index), events.NewMessage)
        task = asyncio.ensure_future(client.start(ID_DICT[f"{i+1}"]["phone_number"]))
        tasks.append(task)

    await asyncio.gather(*tasks)
    ME_ARR = [await client.get_me() for client in clients_array]
    print(f"{len(ME_ARR)} клієнтів ТГ .get_me() завантажено")
    # tasks = []
    # bg_task = asyncio.ensure_future(background_task())
    # tasks.append(bg_task)
    # await asyncio.gather(*tasks)
    tasks = []
    convoy_startup = asyncio.ensure_future(count_convoys_and_start_raid())
    tasks.append(convoy_startup)
    await asyncio.gather(*tasks)   


async def main():
    global ME_ARR
    await start_clients()
    await asyncio.gather(*[client.run_until_disconnected() for client in clients_array])
    
    task = asyncio.create_task(background_task())
    await asyncio.gather(task)


if __name__ == "__main__":
    asyncio.run(main())