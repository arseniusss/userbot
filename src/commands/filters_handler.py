from ..constants_imports.imports import clients_array, userbots_collection, RANDOMBOT_ID
from .shop_buy import buy_something_in_shop
from telethon.tl.functions.messages import GetBotCallbackAnswerRequest
import asyncio
import random
from datetime import timedelta
from typing import List
from ..helper_commands.get_me_arr import get_me_arr
from collections import defaultdict


ME_ARR = []
async def filters_handler(event, client_index: int):
    # TODO: п'ятихвилинна затримка перед тим, як спробувати взяти лут 
    if event.message.from_id is None:
        return

    user_doc = userbots_collection.find_one(
        {
            'index': client_index
        },
    )


    if (user_doc and event.message.chat_id not in user_doc['chats_allowed']):
        return
    message_recieved = event.message
    
    if "Додатковий гумконвой вже в дорозі!" in message_recieved.text and message_recieved.chat_id == user_doc.get('convoys_observe_chat', 0) and message_recieved.from_id.user_id == RANDOMBOT_ID:
        try:
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
        except:
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
        except:
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
        
        if message_recieved.chat_id in user_doc.get("auto_clan_heal", []):
            await clients_array[client_index].send_message(message_recieved.chat_id, '.cl хп')
            await clients_array[client_index].send_message(message_recieved.chat_id, '.cl хп')
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


async def filter_toggle(toggle_parameter: str, toggle_value: str, chat_id: int, client_index: int) -> str:
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
    

async def display_chat_filters(chat_id: int, chosen_bots: List[int]):
    global ME_ARR
    ME_ARR = await get_me_arr(clients_array)
    title_chat = await clients_array[chosen_bots[0]].get_entity(chat_id)
    title_chat = title_chat.title
    response_message = f"Увімкнені фільтри чату {title_chat}:\n\n"
    for i in chosen_bots:
        user_doc = userbots_collection.find_one(
                {
                    'index': i,
                }
            )
        response_message+=f"{ME_ARR[i].first_name}({i+1}): "
        response_message+="🌐" if chat_id in user_doc.get("auto_war", []) else ""
        response_message+="(🔄)" if chat_id in user_doc.get("auto_start_war", []) else ""
        response_message+="⚔️" if chat_id in user_doc.get("auto_battle", []) else ""
        response_message+="(🔄)" if chat_id in user_doc.get("auto_start_battle", []) else ""
        response_message+="💰" if chat_id in user_doc.get("auto_raid", []) else ""
        response_message+="(🔄)" if chat_id in user_doc.get("auto_start_raid", []) else ""
        response_message+="🎰" if chat_id in user_doc.get("auto_loot", []) else ""
        response_message+="🚛" if chat_id in user_doc.get("auto_makima_mode", []) else ""
        response_message+=f"({user_doc.get('convoys_limit', 2)})" if chat_id in user_doc.get("auto_makima_mode", []) else ""
        response_message+="\n"
            
    await clients_array[chosen_bots[0]].send_message(chat_id, response_message)

async def filters_toggle_wrapper_with_response(bots_to_respond, message_args: list[str], chat_id: int, message_id: int):
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
            toggle_result = await filter_toggle("auto_" + toggle_parameter, toggle_value, chat_id, i)
            if toggle_value == "idk":
                toggled_dict[toggle_result].append(i)

        for key, value in toggled_dict.items():
            if len(value):
                response_message+=f"\nбот{'и ' if len(value)!=1 else f'#'}{','.join(map(str, [v+1 for v in value]))} тепер {'НЕ ' if key=='off' else ''}{get_toggle_responses(toggle_parameter, len(value)==1)};" 
            
    
    await clients_array[bots_to_respond[0]].send_message(chat_id, response_message, reply_to=message_id)