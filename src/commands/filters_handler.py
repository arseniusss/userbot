from ..constants_imports.imports import clients_array, userbots_collection, RANDOMBOT_ID
from .shop_buy import buy_something_in_shop
from telethon.tl.functions.messages import GetBotCallbackAnswerRequest
import asyncio
import random
from datetime import timedelta
from typing import List, Optional, Any
from ..helper_commands.get_me_arr import get_me_arr
from collections import defaultdict
from enum import Enum, auto


class FilterSettingEnum(Enum):
    SLEEP = "sleep"
    FILTERS = "filters"
    OBSERBATION = "observation"
    LOOT = "loot"

class FilterValueType(Enum):
    LIST = list
    DICT_NUM = dict
    FLOAT = float
    INT = int
    STR = str
    BOOL = bool


class UserbotFilterSetting:
    def __init__(self, name: str, category: FilterSettingEnum, aliases: Optional[List[str]] = [], value_type: Optional[FilterValueType] = FilterValueType.LIST):
        self.name: str = name
        self.category: FilterSettingEnum = category
        self.aliases: List[str] = aliases
        self.value_type: FilterValueType = value_type


class UserbotFilterManager:
    SETTINGS_FILTERS_LIST : List[UserbotFilterSetting] = [
            UserbotFilterSetting("war_join", FilterSettingEnum.FILTERS, aliases=["war"], value_type=FilterValueType.LIST),
            UserbotFilterSetting("raid_join", FilterSettingEnum.FILTERS, aliases=["raid"], value_type=FilterValueType.LIST),
            UserbotFilterSetting("battle_join", FilterSettingEnum.FILTERS, aliases=["battle"], value_type=FilterValueType.LIST),
            UserbotFilterSetting("horilka_purchase", FilterSettingEnum.FILTERS, aliases=["horilka"], value_type=FilterValueType.LIST),
            UserbotFilterSetting("war_autostart", FilterSettingEnum.FILTERS, aliases=["start_war"], value_type=FilterValueType.LIST),
            UserbotFilterSetting("battle_autostart", FilterSettingEnum.FILTERS, aliases=["start_battle"], value_type=FilterValueType.LIST),
            UserbotFilterSetting("raid_autostart", FilterSettingEnum.FILTERS, aliases=["start_raid"], value_type=FilterValueType.LIST),
            UserbotFilterSetting("clan_heal", FilterSettingEnum.FILTERS, aliases=[], value_type=FilterValueType.LIST),
            UserbotFilterSetting("makima_mode", FilterSettingEnum.FILTERS, aliases=["pizdilka_convoiv"], value_type=FilterValueType.LIST),
            UserbotFilterSetting("pre_battle_sleep", FilterSettingEnum.SLEEP, aliases=["battle_sleep"], value_type=FilterValueType.DICT_NUM),
            UserbotFilterSetting("pre_war_sleep", FilterSettingEnum.SLEEP, aliases=["war_sleep"], value_type=FilterValueType.DICT_NUM),
            UserbotFilterSetting("pre_raid_sleep", FilterSettingEnum.SLEEP, aliases=["raid_sleep"], value_type=FilterValueType.DICT_NUM),
            UserbotFilterSetting("convoys_limit", FilterSettingEnum.FILTERS, aliases=["convoys_limit"], value_type=FilterValueType.INT),
            UserbotFilterSetting("count_convoys", FilterSettingEnum.OBSERBATION, aliases=[], value_type=FilterValueType.INT),
            UserbotFilterSetting("loot_chats_enabled", FilterSettingEnum.LOOT, aliases=["loot"], value_type=FilterValueType.LIST),
            UserbotFilterSetting("feed", FilterSettingEnum.FILTERS, aliases=[], value_type=FilterValueType.STR),
            UserbotFilterSetting("packs_lower_bound", FilterSettingEnum.LOOT, aliases=["packs_lower"], value_type=FilterValueType.INT),
            UserbotFilterSetting("packs_upper_bound", FilterSettingEnum.LOOT, aliases=["packs_upper"], value_type=FilterValueType.INT),
            UserbotFilterSetting("morning_convoy", FilterSettingEnum.FILTERS, aliases=[], value_type=FilterValueType.LIST),
        ]
    def __init__(self):
        pass

    @staticmethod
    def get_filter_setting(name_or_alias: str) -> Optional[UserbotFilterSetting]:
        for setting in UserbotFilterManager.SETTINGS_FILTERS_LIST:
            if setting.name == name_or_alias:
                return setting
            if name_or_alias in setting.aliases:
                return setting
            

ME_ARR = []
async def filters_handler(event, client_index: int):
    # TODO: п'ятихвилинна затримка перед тим, як спробувати взяти лут 
    if event.message.from_id is None:
        return

    user_doc = userbots_collection.find_one({'index': client_index})

    if not user_doc or event.message.chat_id not in user_doc.get('chats_allowed', []):
        return
    
    message_received = event.message

    if message_received.from_id.user_id != RANDOMBOT_ID:
        return
    
    if "Гумконвой прибув" in message_received.text:
        try:
            if message_received.chat_id in user_doc.get("filters", {}).get('morning_convoy', []):
                snatch_message_id = user_doc.get("observation", {}).get('last_raid_id', {}).get(str(message_received.chat_id), 1)
                          
                try:
                    await clients_array[client_index](GetBotCallbackAnswerRequest(
                        message_received.chat_id,
                        snatch_message_id,
                        data='raid_join'
                    ))
                except:
                    pass
            await clients_array[client_index].send_message(message_received.chat_id, "Я намагався зайти в цей рейд", reply_to=snatch_message_id)
    
            userbots_collection.find_one_and_update(
                {'index': client_index},
                {"$inc": {"observation.number_convoys": 1}}
            )
            return
        except:
            pass
    if "Додатковий гумконвой вже в дорозі!" in message_received.text and message_received.chat_id == user_doc.get('observation', {}).get('convoys_observe_chat'):
        try:
            convoy_limit = user_doc.get("filters", {}).get('convoys_limit', 2)
            current_convoys = user_doc.get("filters", {}).get('number_convoys', 0)
            snatch_message_id = user_doc.get("observation", {}).get('last_raid_id', {}).get(str(message_received.chat_id), 1)
            chat_to_observe = user_doc.get("observation", {}).get('convoys_observe_chat')

            if current_convoys + 1 >= convoy_limit and message_received.chat_id in user_doc.get("filters", {}).get('makima_mode', []):                          
                try:
                    await clients_array[client_index](GetBotCallbackAnswerRequest(
                        chat_to_observe,
                        snatch_message_id,
                        data='raid_join'
                    ))
                except:
                    pass
                await clients_array[client_index].send_message(message_received.chat_id, "Я намагався зайти в цей рейд", reply_to=snatch_message_id)
       
            userbots_collection.find_one_and_update(
                {'index': client_index},
                {"$inc": {"observation.number_convoys": 1}}
            )
            return
        except:
            pass
    
    if "Гумконвой розграбовано" in message_received.text and message_received.chat_id == user_doc.get('observation', {}).get('convoys_observe_chat'):
        userbots_collection.find_one_and_update(
            {'index': client_index},
            {"$set": {"observation.number_convoys": 0}}
        )
        return
    
    if "Починається міжчатова битва" in message_received.text and message_received.chat_id in user_doc.get('filters', {}).get('war_join', []):
        try:    
            if message_received.chat_id in user_doc.get('filters', {}).get('horilka_purchase', []):
                await buy_something_in_shop(client_index, "бд")
                await clients_array[client_index].send_message(message_received.chat_id, "Я купив горілку", reply_to=event.message.id)
            
            if message_received.reply_markup and hasattr(message_received.reply_markup, 'rows'):
                for row in message_received.reply_markup.rows:
                    for button in row.buttons:
                        if "міжчатовий бій" in button.text:                       
                            sleep_time = user_doc.get("sleep", {}).get('pre_war_sleep', 0.2 * client_index + random.random())
                            await asyncio.sleep(sleep_time)
                            try:
                                await clients_array[client_index](GetBotCallbackAnswerRequest(
                                    message_received.chat_id,
                                    message_received.id,
                                    data=button.data
                                ))
                            except:
                                pass
                            return
        except:
            pass
    
    if "Починається битва" in message_received.text:
        try:
            if message_received.reply_markup and hasattr(message_received.reply_markup, 'rows') and message_received.chat_id in user_doc.get('filters', {}).get('battle_join', []):
                sleep = user_doc.get("sleep", {}).get('pre_battle_sleep', 0.7 + 0.2 * client_index + random.random())
                await asyncio.sleep(sleep + random.random() * 0.4)
                await clients_array[client_index](GetBotCallbackAnswerRequest(
                    message_received.chat_id,
                    message_received.id,
                    data='join'
                ))
                return
        except:
            pass
        userbots_collection.find_one_and_update(
            {"index": client_index},
            {"$set": {f"observation.last_battle_id.{message_received.chat_id}": message_received.id}}
        )
    
    if "Починається рейд" in message_received.text:
        try:
            if message_received.chat_id in user_doc.get('filters', {}).get('raid_join', []) and message_received.reply_markup and hasattr(message_received.reply_markup, 'rows'):
                sleep = user_doc.get("sleep", {}).get('pre_raid_sleep', 0.7 + 0.2 * client_index + random.random())
                await asyncio.sleep(sleep)
                await clients_array[client_index](GetBotCallbackAnswerRequest(
                    message_received.chat_id,
                    message_received.id,
                    data='raid_join'
                ))
                return
            userbots_collection.find_one_and_update(
                {"index": client_index},
                {"$set": {f"observation.last_raid_id.{message_received.chat_id}": message_received.id}}
            )
        except:
            pass
    
    if "Міжчатова битва русаків завершена!" in message_received.text and message_received.chat_id in user_doc.get('filters', {}).get('war_autostart', []):
        await clients_array[client_index].send_message(message_received.chat_id, '/war')
        return
    
    if ("/battle" in message_received.text or "завершена" in message_received.text) and message_received.chat_id in user_doc.get('filters', {}).get('battle_autostart', []) and not message_received.text.startswith("/battle") and "Війна" not in message_received.text:
        await clients_array[client_index].send_message(message_received.chat_id, '/battle')
        return
    
    if 'рейди недоступні' in message_received.text and message_received.chat_id in user_doc.get('filters', {}).get('raid_autostart', []):
        await clients_array[client_index].send_message(message_received.chat_id, '/raid', schedule=timedelta(seconds=8*3600 + random.randint(7, 10)))
        return
    
    if "Проведено рейд" in message_received.text or "Русаки приїхали грабувати" in message_received.text:
        if message_received.chat_id in user_doc.get('filters', {}).get('raid_autostart', []):
            if "наступний рейд" in message_received.text or "реванш" in message_received.text:
                await clients_array[client_index].send_message(message_received.chat_id, '/raid', schedule=timedelta(seconds=5 + random.randint(5, 10)))
            else:
                await clients_array[client_index].send_message(message_received.chat_id, '/raid', schedule=timedelta(seconds=3600 + random.randint(10, 20)))
        
        if message_received.chat_id == user_doc.get("guard_chat", 0) and user_doc.get('filters', {}).get('clan_heal', False) and '-100' in message_received.text:
            await clients_array[client_index].send_message(message_received.chat_id, '.cl хп', schedule=timedelta(seconds=3 + random.randint(5, 7)))
            await clients_array[client_index].send_message(message_received.chat_id, '.cl хп', schedule=timedelta(seconds=3 + random.randint(7, 10)))
        
        if message_received.chat_id in user_doc.get('loot', {}).get('loot_chats_enabled', []):
            if message_received.reply_markup and hasattr(message_received.reply_markup, 'rows'):
                for row in message_received.reply_markup.rows:
                    for button in row.buttons:
                        try:
                            await clients_array[client_index](GetBotCallbackAnswerRequest(
                                message_received.chat_id,
                                message_received.id,
                                data=button.data
                            ))
                            await asyncio.sleep(0.05)
                        except:
                            pass
                await clients_array[client_index].send_message(message_received.chat_id, '+', reply_to=message_received.id) 
                if any(item in message_received.text for item in ['🍝', '🍛', '🍜', '🥗', '🌭']):
                    if user_doc.get('filters', {}).get("feed", "off") == "on":
                        await clients_array[client_index].send_message(event.message.chat_id, '/feed')


async def filter_toggle(toggle_parameter: str, toggle_value: str, chat_id: int, client_index: int) -> str|None:
    user_doc = userbots_collection.find_one(
        {
            'index': client_index,
        }
    )

    if user_doc is None:
        return
    
    filter: UserbotFilterSetting|None = UserbotFilterManager.get_filter_setting(toggle_parameter)
    if filter is None:
        return
    
    if filter.value_type == FilterValueType.LIST:
        toggle_arr: List = user_doc.get(f"{filter.category}.{filter.name}", [])
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
                    f"{filter.category.value}.{filter.name}": toggle_arr,
                }
            },
            upsert=True,
        )
        if toggle_value=='idk':
            return return_value
    
    elif filter.value_type == FilterValueType.FLOAT or filter.value_type == FilterValueType.INT or filter.value_type == FilterValueType.STR:
        userbots_collection.find_one_and_update(
            {
                'index': client_index,
            },
            {
                "$set": {
                    f"{filter.category.value}.{filter.name}": filter.value_type.value(toggle_value),
                }
            },
            upsert=True,
        )
    elif filter.value_type == FilterValueType.DICT_NUM:
        toggle_arr: List = user_doc.get(f"{filter.category}.{filter.name}", [])
        userbots_collection.find_one_and_update(
            {
                'index': client_index,
            },
            {
                "$set": {
                    f"{filter.category.value}.{filter.name}.{chat_id}": float(toggle_value),
                }
            },
            upsert=True,
        )
    

async def display_chat_filters(chat_id: int, chosen_bots: List[int]) -> None:
    global ME_ARR
    ME_ARR = await get_me_arr(clients_array)
    title_chat = await clients_array[chosen_bots[0]].get_entity(chat_id)
    title_chat = title_chat.title
    response_message = f"Увімкнені фільтри чату {title_chat}:"
    response_rawest_outline_paragraphs = []
    response_intermediary_dict = defaultdict(dict)

    for i in chosen_bots:
        user_doc = userbots_collection.find_one({'index': i})

        filters_category = user_doc.get("filters", {})
        for f in filters_category:
            if isinstance(filters_category[f], dict):
                for key, value in filters_category[f].items():
                    response_intermediary_dict[f].setdefault(i, {})[key] = value
            else:
                response_intermediary_dict[f][i] = filters_category[f]

        sleep_category = user_doc.get("sleep", {})
        for f in sleep_category:
            if isinstance(sleep_category[f], dict):
                for key, value in sleep_category[f].items():
                    response_intermediary_dict[f].setdefault(i, {})[key] = value
            else:
                response_intermediary_dict[f][i] = sleep_category[f]

        observation_category = user_doc.get("observation", {})
        for f in observation_category:
            if isinstance(observation_category[f], dict):
                for key, value in observation_category[f].items():
                    response_intermediary_dict[f].setdefault(i, {})[key] = value
            else:
                response_intermediary_dict[f][i] = observation_category[f]

        loot_category = user_doc.get("loot", {})
        for f in loot_category:
            if isinstance(loot_category[f], dict):
                for key, value in loot_category[f].items():
                    response_intermediary_dict[f].setdefault(i, {})[key] = value
            else:
                response_intermediary_dict[f][i] = loot_category[f]
    
    print(response_intermediary_dict)

    war_response_enabled, war_response_message = False, ''
    if response_intermediary_dict.get('war_autostart'):
        respective_bots = [bot+1 for bot in chosen_bots if chat_id in response_intermediary_dict.get('war_autostart', {}).get(bot, [])]
        if respective_bots: 
            war_response_message += '\nㅤ🔄󠀠Автоматично починає(-ють): ' + ', '.join(map(str, respective_bots))
            war_response_enabled = True
    if response_intermediary_dict.get('war_join'):
        respective_bots = [bot+1 for bot in chosen_bots if chat_id in response_intermediary_dict.get('war_join', {}).get(bot, [])]
        if respective_bots: 
            war_response_message+='\nㅤ➡️󠀠Автоматично заходять(-ить): ' + ', '.join(map(str, respective_bots))
            war_response_enabled = True
    if response_intermediary_dict.get('pre_war_sleep'):
        war_response_message+='\nㅤ💤Чекають перед заходом: '
        for bot in chosen_bots:
            user_doc = userbots_collection.find_one({'index': bot})
            sleep_time = response_intermediary_dict.get('pre_war_sleep', {}).get(bot, {}).get(f'{chat_id}', -1)
            if sleep_time != -1:
                war_response_message += f'№{bot+1} ({sleep_time} c.);'
                war_response_enabled = True
    if response_intermediary_dict.get('horilka_purchase'):
        respective_bots = [bot+1 for bot in chosen_bots if chat_id in response_intermediary_dict.get('horilka_purchase', {}).get(bot, [])]
        if respective_bots: 
            war_response_message+='\nㅤ☢️Автоматично купує(-ють) горілку: ' + ', '.join(map(str, respective_bots))
            war_response_enabled = True

    if war_response_enabled:
        response_message+=('\n\n🌐МІЖЧАТ🌐'+war_response_message)


    raid_response_enabled, raid_response_message = False, ''
    if response_intermediary_dict.get('raid_autostart'):
        respective_bots = [bot+1 for bot in chosen_bots if chat_id in response_intermediary_dict.get('raid_autostart', {}).get(bot, [])]
        if respective_bots: 
            raid_response_message += '\nㅤ🔄󠀠Автоматично починає(-ють): ' + ', '.join(map(str, respective_bots))
            raid_response_enabled = True
    if response_intermediary_dict.get('raid_join'):
        respective_bots = [bot+1 for bot in chosen_bots if chat_id in response_intermediary_dict.get('raid_join', {}).get(bot, [])]
        if respective_bots: 
            raid_response_message+='\nㅤ➡️󠀠Автоматично заходять(-ить): ' + ', '.join(map(str, respective_bots))
            raid_response_enabled = True
    if response_intermediary_dict.get('pre_raid_sleep'):
        raid_response_message+='\nㅤ💤Чекають перед заходом: '
        for bot in chosen_bots:
            user_doc = userbots_collection.find_one({'index': bot})
            sleep_time = response_intermediary_dict.get('pre_raid_sleep', {}).get(bot, {}).get(f'{chat_id}', -1)
            if sleep_time != -1:
                raid_response_message += f'№{bot+1} ({sleep_time} c.);'
                raid_response_enabled = True
    if response_intermediary_dict.get('makima_mode'):
        respective_bots = []
        for bot in chosen_bots:
            user_doc = userbots_collection.find_one({'index': bot})
            if chat_id in response_intermediary_dict['makima_mode'].get(bot, []):
                convoys_limit = user_doc.get('filters', {}).get('convoys_limit', -1)
                respective_bots.append(f"{bot+1}" + (f'(від {convoys_limit})' if convoys_limit!=-1 else ''))

        if respective_bots:
            raid_response_message += "\nㅤ🚛Автоматично пиздять(-ить) конвої: " + ', '.join(respective_bots)
            raid_response_enabled = True
    if response_intermediary_dict.get('makima_mode'):
        respective_bots = []
        for bot in chosen_bots:
            user_doc = userbots_collection.find_one({'index': bot})
            if chat_id in response_intermediary_dict['morning_convoy'].get(bot, []):
                respective_bots.append(f"{bot+1};")

        if respective_bots:
            raid_response_message += "\nㅤ🚚Автоматично пиздять(-ить) ранкові конвої: " + ', '.join(respective_bots)
            raid_response_enabled = True

    if response_intermediary_dict.get('loot_pickup'):
        respective_bots = []
        for bot in chosen_bots:
            user_doc = userbots_collection.find_one({'index': bot})
            if chat_id in response_intermediary_dict['loot_pickup'].get(bot, []):
                packs_lower = user_doc.get('loot', {}).get('packs_lower_bound', 0)
                packs_upper = user_doc.get('loot', {}).get('packs_upper_bound', '∞')

                respective_bots.append(f"{bot+1}" + (f'(від {packs_lower} до {packs_upper}📦);'))

        if respective_bots:
            raid_response_message += "\nㅤ🎰Автоматично краде(-уть) лут: " + ', '.join(respective_bots)
            raid_response_enabled = True

    if raid_response_enabled:
        response_message+=('\n\n💰РЕЙД💰'+raid_response_message)


    battle_response_enabled, battle_response_message = False, ''
    if response_intermediary_dict.get('battle_autostart'):
        respective_bots = [bot+1 for bot in chosen_bots if chat_id in response_intermediary_dict.get('battle_autostart', {}).get(bot, [])]
        if respective_bots: 
            battle_response_message += '\nㅤ🔄󠀠Автоматично починає(-ють): ' + ', '.join(map(str, respective_bots))
            battle_response_enabled = True
    if response_intermediary_dict.get('battle_join'):
        respective_bots = [bot+1 for bot in chosen_bots if chat_id in response_intermediary_dict.get('battle_join', {}).get(bot, [])]
        if respective_bots: 
            battle_response_message+='\nㅤ➡️󠀠Автоматично заходять(-ить): ' + ', '.join(map(str, respective_bots))
            battle_response_enabled = True
    if response_intermediary_dict.get('pre_battle_sleep'):
        battle_response_message+='\nㅤ💤Чекають перед заходом: '
        for bot in chosen_bots:
            user_doc = userbots_collection.find_one({'index': bot})
            sleep_time = response_intermediary_dict.get('pre_battle_sleep', {}).get(bot, {}).get(f'{chat_id}', -1)
            if sleep_time != -1:
                battle_response_message += f'№{bot+1} ({sleep_time} c.);'
                battle_response_enabled = True

    if battle_response_enabled:
        response_message+=('\n\n⚔️МАСОВА БИТВА⚔️'+battle_response_message)

    await clients_array[chosen_bots[0]].send_message(chat_id, response_message)

async def filters_toggle_wrapper_with_response(bots_to_respond: List[int], message_args: list[str], chat_id: int, message_id: int) -> None:
    response_message = f"Фільтри чату змінено: бот{' #' if len(bots_to_respond) == 1 else 'и '}" + ",".join(map(str, [bot+1 for bot in bots_to_respond])) + f" {'має' if len(bots_to_respond) == 1 else 'мають'} інші налаштування. Перевірте через .cl f" 

    for bot_index in bots_to_respond:
        await filter_toggle(message_args[1], "idk" if len(message_args)<=2 else message_args[2], chat_id, bot_index)
    
    await clients_array[bots_to_respond[0]].send_message(chat_id, response_message, reply_to=message_id)