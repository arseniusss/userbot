from telethon import events
from telethon.tl.types import InputPeerChat
import asyncio
from src.constants_imports.constants import ID_DICT, WINESRA_ID
from src.constants_imports.imports import userbots_collection, clients_array, NUMBER_OF_ACCOUNTS
from src.commands.filters_handler import filters_handler, display_chat_filters, filters_toggle_wrapper_with_response 
from src.commands.shop_buy import buy_something_in_shop, BUY_OPTIONS
from src.commands.guard_commands import guard, display_guard_chats, add_guard_chat, get_guard_status
from src.commands.dm_fetch_info import display_rusaks, display_acc, display_rusak_classes
from src.commands.general_chat_commands import get_curr_chat_activities, crash_battle
from src.commands.click import click_on_message
from src.commands.r_help import send_help_message
from src.commands.admin_commands import add_admin, add_chat
from src.commands.convoys_handler import observe_convoys, count_convoys_and_start_raid, convoys_encountered
from src.helper_commands.determine_bots import determine_clients_to_respond, get_first_bots_that_are_in_channel
from src.commands.randombot_inline_handler import duel_handler, tournament_handler


ME_ARR = []

async def message_handler(event, client_index: int) -> None:
    global COMMANDS_WITH_ONE_ANSWER_MESSAGE, ME_ARR, WINESRA_ID
    message_recieved = event.message
    await filters_handler(event, client_index)

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
    
    bots_to_respond = await determine_clients_to_respond(event, ME_ARR, client_index)
    if client_index not in bots_to_respond:
        return
        
    message_args = message_recieved.text.split()
    if len(message_recieved.text.split()) >=2:
        if client_index!=bots_to_respond[0] and client_index!=0:
            return
        if str(message_args[1]).startswith("/"):
            string_to_send = ' '.join(message_args[1:])
            banned_commands = ['/openpack', 'donate_shop']
            if message_args[1] in banned_commands:
                await clients_array[bots_to_respond[0]].send_message(message_recieved.chat_id, f"іДі нахуй, я жадібний", reply_to=message_recieved.id)
                return
            for i in bots_to_respond:
                await clients_array[i].send_message(message_recieved.chat_id, string_to_send)
        if message_args[1] in BUY_OPTIONS:
            tasks = []
            for i in bots_to_respond:
                tasks.append(buy_something_in_shop(i, message_args[1]))
            await asyncio.gather(*tasks)
            await clients_array[bots_to_respond[0]].send_message(message_recieved.chat_id, f"Я купив {message_args[1]} на {len(bots_to_respond)} аккаунтах", reply_to=message_recieved.id)
        
        if message_args[1] in ["rusak", "русак", "r", 'р']: 
            # TODO: параметр -2 для другого русака/другого класу
            await display_rusaks(bots_to_respond, ME_ARR, event.message.chat_id, event.message.id)

        if message_args[1] in ["account", "акк", 'acc', 'а', 'a']:
            await display_acc(bots_to_respond, ME_ARR, event.message.chat_id, event.message.id)

        elif message_args[1] == "observe_convoys":
            await observe_convoys(bots_to_respond, event.message.chat_id, event.message.id)

        elif message_args[1] == "addchat":
            # TODO: все те саме, тільки з remove
            await add_chat(bots_to_respond, ME_ARR, event.message.chat_id, event.message.id)                    

        elif message_args[1] == "addadmin":
            await add_admin(bots_to_respond, ME_ARR, event.message)

        elif message_args[1] == "add_guard_chat":
            await add_guard_chat(bots_to_respond, ME_ARR, event.message.chat_id, event.message.id)
        
        elif message_args[1] in ["guard", "g"]:
            # TODO: потім додати багатопоточність
            await guard(bots_to_respond)
        
        elif message_args[1] == "class":
            await display_rusak_classes(bots_to_respond, ME_ARR, event.message.chat_od, event.messsage.id)
        
        elif message_args[1] in ["war", "battle", "loot", "start_war", "start_battle", "raid", "start_raid", "battle_sleep", "count_convoys", "makima_mode", "convoys_limit"]:
            await filters_toggle_wrapper_with_response(bots_to_respond, message_args, event.message.chat_id, event.message.id)
        
        elif message_args[1] in ["filters", "фільтри", "f", 'ф']:
            #TODO: якийсь нормальний /i
            #TODO: admins
            #TODO: норм оформлення, щоб автоматично викликалось тільки для .cl
            await display_chat_filters(event.message.chat_id, bots_to_respond)
        
        elif message_args[1] in ["клік", "тиць", ".", "👉", "☝️", "👆"]:
            # TODO: refresh - видалення поточного міжчату, два рази надіслати вар, те ж саме з битвами
            await click_on_message(bots_to_respond, message_args, message_recieved)

        elif message_args[1] in ["дуель", "duel", "d", "д"]:
            await duel_handler(bots_to_respond, message_args, event.message.chat_id)
        elif message_args[1] in ["турнір", "tour", "т", "t"]:
            await tournament_handler(bots_to_respond, message_args, event.message.chat_id)

    else:
        user_ids = await get_first_bots_that_are_in_channel(client_index, ME_ARR, event.message.chat_id, event.message.id)
        if message_recieved.text == ".status":
            status_list = [f"{'🟢' if clients_array[i].is_connected() else '🔴'} {ME_ARR[i].first_name + ' ' + ME_ARR[i].last_name if ME_ARR[i].last_name else ME_ARR[i].first_name}" for i in range(NUMBER_OF_ACCOUNTS)]
            status_message = "Увімкнені боти:\n\n" + "\n".join(status_list)
            await clients_array[user_ids[0]].send_message(event.message.chat_id, status_message)
            return

        elif message_recieved.text == ".guards":
            await get_guard_status(ME_ARR, event.message.chat_id, event.message.id)
        
        elif message_recieved.text == '.chats':
            await display_guard_chats(bots_to_respond, ME_ARR, event.message.chat_id, event.message.id)

        elif message_recieved.text == ".info":
            # TODO: щоб показувало скільки часу тому була остання битва/міжчат/рейд
            await get_curr_chat_activities(bots_to_respond[0], event.message.chat_id, event.message.id)

        elif message_recieved.text == ".crash":
            if client_index!=user_ids[0]:
                return
            await crash_battle(bots_to_respond[0], event.message.chat_id)

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
            await send_help_message(bots_to_respond[0], event.message.chat_id, event.message.id)

        elif message_recieved.text in ["конвой", "камвой", ".convoy"]:
            await convoys_encountered(bots_to_respond[0], event.message.chat_id, event.message.id)


async def start_clients():
    global ME_ARR
    tasks = []
    for i, client in enumerate(clients_array):
        client.add_event_handler(lambda e, index=i: message_handler(e, index), events.NewMessage)
        task = asyncio.ensure_future(client.start(ID_DICT[f"{i+1}"]["phone_number"]))
        tasks.append(task)

    await asyncio.gather(*tasks)

    tasks = [client.get_me() for client in clients_array]
    ME_ARR = await asyncio.gather(*tasks)

    for i in range(NUMBER_OF_ACCOUNTS):
        print(f"Завантажую переписки {ME_ARR[i].first_name}")
        client = clients_array[i]
        dialogs = await client.get_dialogs()
        
        for dialog in dialogs:
            if isinstance(dialog.entity, InputPeerChat):
                await client.get_participants(dialog.entity)
    
    print("Я зібрав інформацію про клієнтів")


    tasks = []
    convoy_startup = asyncio.ensure_future(count_convoys_and_start_raid())
    tasks.append(convoy_startup)
    await asyncio.gather(*tasks)   


async def main():
    global ME_ARR
    await start_clients()
    await asyncio.gather(*[client.run_until_disconnected() for client in clients_array])


if __name__ == "__main__":
    asyncio.run(main())