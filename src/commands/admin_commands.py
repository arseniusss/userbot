from ..constants_imports.imports import userbots_collection, clients_array
from ..constants_imports.constants import WINESRA_ID


async def add_chat(bots_to_respond: list, ME_ARR: list, chat_id: int, message_id: int):
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
                    'chats_allowed': [chat_id],
                    'admins': [WINESRA_ID],
                }
            )
        else: 
            current_chats_allowed = user_doc.get('chats_allowed', [])
            if chat_id not in current_chats_allowed:
                current_chats_allowed.append(chat_id)
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
    await clients_array[bots_to_respond[0]].send_message(chat_id, f"✅ {botsadded} бот(и/ів) успішно додали чат {chat_id} до списку дозволених чатів", reply_to=message_id)                          

async def add_admin(bots_to_respond: list, ME_ARR: list, message_recieved):
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
