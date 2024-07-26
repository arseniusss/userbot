import asyncio
import random
from ..helper_commands.emoji_handler import rusak_stats_map
from ..constants_imports.imports import clients_array, RANDOMBOT_ID
from typing import List
from collections import defaultdict


async def display_acc(bots_to_respond: List[int], ME_ARR: List, chat_id: int, message_id: int):
    message_to_send = "💵📦🧂🌀🌟Стати аккаунтів русаків:\n"
    total_dict = {}
    async def get_acc_info(client_index: int) -> dict[str, int]:
        await clients_array[client_index].send_message(RANDOMBOT_ID, '/account')
        await asyncio.sleep(0.4)
        random_messages = await clients_array[client_index].get_messages(RANDOMBOT_ID, from_user=RANDOMBOT_ID, search="Ізострічка:", limit=1)
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
    await clients_array[bots_to_respond[0]].send_message(chat_id, message_to_send, reply_to=message_id)

async def display_rusaks(bots_to_respond: list[int], ME_ARR: list, chat_id: int, message_id: int):
    # TODO: параметр -2 для другого русака/другого класу
    message_to_send = "📊Стати обраних русаків:\n"

    async def get_acc_info(client_index: int, classes_dict: str) -> dict[str, int]:
        await clients_array[client_index].send_message(RANDOMBOT_ID, '/rusak')
        classes_dict[client_index] = '✖️'
        await asyncio.sleep(0.5)
        random_messages = await clients_array[client_index].get_messages(RANDOMBOT_ID, from_user=RANDOMBOT_ID, search="Твій русак", limit=1)
        message = random_messages[0]
        
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

    await clients_array[bots_to_respond[0]].send_message(chat_id, message_to_send, reply_to=message_id)


async def display_rusak_classes(bots_to_respond: list[int], ME_ARR: list, chat_id: int, message_id: int):
    response_message = f"Класи русаків - поточний (додатковий):\n"
    for i in bots_to_respond:
        emoji_primary, emoji_secondary = "✖️", "✖️"
        await clients_array[i].send_message(RANDOMBOT_ID, '/rusak')
        await asyncio.sleep(0.4)
        random_messages = await clients_array[i].get_messages(RANDOMBOT_ID, from_user=RANDOMBOT_ID, search="Твій русак", limit=1)
        for message in random_messages:
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
    await clients_array[bots_to_respond[0]].send_message(chat_id, response_message, reply_to=message_id)


async def display_inventory(bots_to_respond: list[int], ME_ARR: list, chat_id: int, message_id: int):
    message_to_send = "🗡🛡🧪🎩Інвентарі аккаунтів русаків:\n"
    inventory_dict = defaultdict(str)
    async def get_inv_info(client_index: int) -> dict[str, int]:
        await clients_array[client_index].send_message(RANDOMBOT_ID, '/i')
        await asyncio.sleep(0.4)
        random_messages = await clients_array[client_index].get_messages(RANDOMBOT_ID, from_user=RANDOMBOT_ID, search="Шапка:")
        
        message = random_messages[0]
        lines = message.text.split("\n")
        i = 0
        emoji_list = ['🗡', '🛡', '🧪', '🎩']
        items_processed = 0
        while i < len(lines):
            line = lines[i]
            item = line[line.find(': ')+2:]
            if item == '[Порожньо]':
                strength = ''
                i+=1
            else:
                strength = lines[i+1][lines[i+1].find(": ")+2:]
                i+=2
            inventory_dict[client_index] += f"{emoji_list[items_processed]}{item}({strength}); "
            items_processed += 1
        
    tasks = []
    for i in bots_to_respond:
        task = asyncio.create_task(get_inv_info(i))
        tasks.append(task)
    
    await asyncio.gather(*tasks, return_exceptions=True)

    for i in bots_to_respond:
        message_to_send+=f"\n{ME_ARR[i].first_name}({i+1}): {inventory_dict[i]}"

    await clients_array[bots_to_respond[0]].send_message(chat_id, message_to_send, reply_to=message_id)


async def display_status(bots_to_respond: list[int], ME_ARR: list, chat_id: int, message_id: int):
    message_to_send = "🟥🟩Стасус аккаунтів русаків:\n"
    inventory_dict = defaultdict(str)
    async def get_status_info(client_index: int) -> dict[str, int]:
        await clients_array[client_index].send_message(RANDOMBOT_ID, '/status')
        await asyncio.sleep(0.4)
        random_messages = await clients_array[client_index].get_messages(RANDOMBOT_ID, from_user=RANDOMBOT_ID, search="/daily")
        
        message = random_messages[0]
        lines = message.text.split("\n")
        for i in range(len(lines)):
            line = lines[i]
            if not ('🟥' in line or '🟩' in line or 'Дуелі' in line):
                continue

            if 'Дуелі' not in line:
                inventory_dict[client_index] += f"{line} "
            else:
                inventory_dict[client_index] += f";⌛️дуелі: {line[line.find(': ')+2:line.find('/')]};"
            
        
    tasks = []
    for i in bots_to_respond:
        task = asyncio.create_task(get_status_info(i))
        tasks.append(task)
    
    await asyncio.gather(*tasks, return_exceptions=True)

    for i in bots_to_respond:
        message_to_send+=f"\n{ME_ARR[i].first_name}({i+1}): {inventory_dict[i]}"

    await clients_array[bots_to_respond[0]].send_message(chat_id, message_to_send, reply_to=message_id, link_preview=False, clear_draft=True)