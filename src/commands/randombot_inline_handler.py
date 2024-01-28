from ..constants_imports.imports import clients_array, RANDOMBOT_ID
from typing import List


async def duel_handler(bots_to_respond: List[int], message_args: list[str], chat_id: int):
    try:
        number_of_duels = int(message_args[2]) if len(message_args) >= 3 else 1
        for i in bots_to_respond:
            results = await clients_array[i].inline_query(RANDOMBOT_ID, '')
            for _ in range(number_of_duels):
                await results[0].click(chat_id)
    except Exception:
        pass

async def tournament_handler(bots_to_respond: List[int], message_args: list[str], chat_id: int):
    try:
        number_of_tournaments = int(message_args[2]) if len(message_args) >= 3 else 1
        for i in bots_to_respond:
            results = await clients_array[i].inline_query(RANDOMBOT_ID, '&')
            for _ in range(number_of_tournaments):
                await results[2].click(chat_id)
    except Exception:
        pass