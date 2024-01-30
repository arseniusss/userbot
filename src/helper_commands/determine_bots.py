from ..constants_imports.imports import clients_array, userbots_collection, NUMBER_OF_ACCOUNTS


COMMANDS_WITH_ONE_ANSWER_MESSAGE = ["status", "guards", "info", "chats", "stats"]
WINESRA_COMMANDS = ["addchat", "addadmin", "add_guard_chat"]


async def get_first_bots_that_are_in_channel(client_index: int, ME_ARR: list, chat_id: int, limit: int = 1) -> list:
    try:
        participants_list = await clients_array[client_index].get_participants(chat_id)

        user_ids = [participant.id for participant in participants_list]

        result_arr = []
        for id in user_ids:
            if len(result_arr) >= limit:
                return result_arr
            
            for j in range(NUMBER_OF_ACCOUNTS):
                if ME_ARR[j].id == id:
                    result_arr.append(j)
                    break
        return result_arr   
    except:
        return []


async def determine_clients_to_respond(event, ME_ARR: list, client_index: int) -> list[int]:
    message = event.message
    if not hasattr(event.message, 'text'):
        return []
    if len(event.message.text) <= 1:
        return []
    if message.text[1:] in COMMANDS_WITH_ONE_ANSWER_MESSAGE:
        id = await get_first_bots_that_are_in_channel(client_index, ME_ARR, event.message.chat_id)
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