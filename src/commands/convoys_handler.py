from ..constants_imports.imports import clients_array, userbots_collection, NUMBER_OF_ACCOUNTS, RANDOMBOT_ID
from typing import List
import asyncio


async def observe_convoys(bots_to_respond: List[int], chat_id: int, message_id: int):    
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
                        'convoys_observe_chat': chat_id,
                    }   
                }
            )

async def count_convoys_and_start_raid():
    for i in range(NUMBER_OF_ACCOUNTS):
        user_doc = userbots_collection.find_one(
            {
                'index': i,
            }
        )
        if user_doc is not None:
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
        if start_raid_arr:
            for idx in start_raid_arr:
                await clients_array[i].send_message(idx, '/raid')

async def convoys_encountered(client_index: int, chat_id: int, message_id: int):
    user_doc = userbots_collection.find_one(
        {
            'index': client_index,
        }
    )
    chat_to_observe = user_doc.get("convoys_observe_chat", None)
    number_convoys = user_doc.get("number_convoys", 0)
    convoy_looted_msg = await clients_array[client_index].get_messages(chat_to_observe, search='Гумконвой розграбовано', from_user=RANDOMBOT_ID)
    
    id = convoy_looted_msg[0].id
    
    await clients_array[0].send_message(chat_id, f"Я нарахував {number_convoys} конвоїв, розграбували тут.", reply_to=id)