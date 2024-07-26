from ..constants_imports.imports import clients_array, RANDOMBOT_ID
from telethon.tl.functions.messages import GetBotCallbackAnswerRequest


BUY_OPTIONS = ["хп", "бд"] 
async def buy_something_in_shop(client_index: int, stuff_to_buy: str, quantity: int = 1) -> None:
    if stuff_to_buy not in BUY_OPTIONS:
        return False
    # TODO: додати ще щось для закупівлі
    await clients_array[client_index].send_message(RANDOMBOT_ID, '/shop')
    client = clients_array[client_index]
    response = await client.get_messages(RANDOMBOT_ID, from_user=RANDOMBOT_ID, search='Горілка "Козаки"', limit=1)
    if stuff_to_buy == "бд":
        # TODO: перевірки
        if response[0].reply_markup is not None and hasattr(response[0].reply_markup, 'rows'):
            try:
                await client(GetBotCallbackAnswerRequest(
                    response[0].chat_id,
                    response[0].id,
                    data='5_vodka'
                ))
                return
            except:
                pass
    elif stuff_to_buy == "хп":
        # TODO: перевірки
        if response[0].reply_markup is not None and hasattr(response[0].reply_markup, 'rows'):
            try:
                await client(GetBotCallbackAnswerRequest(
                    response[0].chat_id,
                    response[0].id,
                    data='aid_kit'
                ))
                return
            except:
                pass