from telethon.sync import TelegramClient
from telethon.sync import events
from telethon.tl.functions.messages import GetBotCallbackAnswerRequest
from telethon.errors.rpcerrorlist import BotResponseTimeoutError
import asyncio
import random
import re

# Твої дані бота і номер телефону, витащені з телеграму
api_id = 10439443
api_hash = '2e780917ebaa32ded4269e5a4f14cf3a'
phone_number = '+380662706287'
# Чат, на який воно має реагувати
MY_CHAT_ID = -1001914710554

client = TelegramClient('1', api_id, api_hash)

shit_solution = True
i = 0
num_convoys = 0
BIH_PES = -1001973237747
PRIVATE_LOGS_CHAT = -1001876663091
RANDOMBOT_ID = 6277866886

SVYNARNYK = -1001926939989

MY_GROUP = -1001914710554
shit_solution, packs_opened = True, 0

async def buy_sugar(myclient: TelegramClient, randombot_id: int|str):
    await myclient.send_message(randombot_id, '/swap')
    await asyncio.sleep(0.5)
    await myclient.send_message(randombot_id, '/clan_shop')
    await asyncio.sleep(0.5)
    random_messages = await myclient.get_messages(RANDOMBOT_ID, search='Список доступних товарів')
    for message in random_messages:
        if "🏬 Список доступних товарів:" in message.text:
            if hasattr(message.reply_markup, 'rows'):
                for row in message.reply_markup.rows:
                    for button in row.buttons:
                        if "Цукор" in button.text:                          
                            await asyncio.sleep(0.1)
                            try:
                                await client(GetBotCallbackAnswerRequest(
                                    RANDOMBOT_ID,
                                    message.id,
                                    data=button.data
                                ))
                            except Exception as e:
                                print(e)
    await myclient.send_message(randombot_id, '/i')
    await asyncio.sleep(0.5)
    random_messages2 = await myclient.get_messages(RANDOMBOT_ID, limit=1)
    for message in random_messages2:
        if "🗡 Зброя:" in message.text:
            if hasattr(message.reply_markup, 'rows'):
                for row in message.reply_markup.rows:
                    for button in row.buttons:
                        if "🌀" in button.text:
                            try:
                                # Click the button
                                await client(GetBotCallbackAnswerRequest(
                                    RANDOMBOT_ID,
                                    message.id,
                                    data=button.data
                                ))
                                break
                            except Exception as e:
                                print(e)                         
                            
    await asyncio.sleep(0.4+random.random()*0.6)
    random_messages3 = await myclient.get_messages(RANDOMBOT_ID, limit=1)
    for message in random_messages3:
        if "🌀 Ізострічка:" in message.text and hasattr(message.reply_markup, 'rows'):
            for row in message.reply_markup.rows:
                for button in row.buttons:
                    if "Цукор" in button.text:
                        await client(GetBotCallbackAnswerRequest(
                                    RANDOMBOT_ID,
                                    message.id,
                                    data=button.data
                                ))
                        break
    
    await myclient.send_message(randombot_id, '/swap')
    
    return None
num_packs = 10
@client.on(events.NewMessage())
async def handle_start_typing(event: events.NewMessage):
    global shit_solution
    global i
    global num_convoys
    message = event.message
    if message.chat_id == MY_GROUP:
        global shit_solution, packs_opened, num_packs
        if message.sender_id == RANDOMBOT_ID:
            if "#loot" not in message.text and "Гаманець і їжа" not in message.text:
                await message.delete()
        if 'Гаманець і їжа' in message.text:
            shit_solution = False
            await client.send_message(message.chat_id, "🍛🍛🍛 Я ЗНАЙШОВ ГОДУВАЧКУ 🍛🍛🍛")
        elif 'почисть' in message.text:
            num_to_clear = int(message.text.split()[1])
            my_messages = await client.get_messages(MY_CHAT_ID, limit=num_to_clear)
            for message_sent in my_messages:
                if "/openpack" in message_sent.text or "почисть" in message_sent.text or 'packs' in message_sent.text:
                    await message_sent.delete()
        elif 'packs' in message.text:
            shit_solution = True
            num_packs = int(message.text.split()[1])
            while shit_solution == True:
                await client.send_message(MY_CHAT_ID, f'/openpack {num_packs}')
                await asyncio.sleep(0.6666666+random.random()*0.271828459045+random.random()*0.314159265)
                packs_opened += num_packs
        elif "купи цукор" in message.text:
            await buy_sugar(client, RANDOMBOT_ID)

with client:
    client.start(phone_number)
    my_chats = client.get_dialogs()
    for chat in my_chats:
        if chat.id == 6277866886:
            RANDOM_CHAT = chat
    client.run_until_disconnected()