from ..constants_imports.imports import clients_array
from typing import List
from telethon.tl.functions.messages import GetBotCallbackAnswerRequest


async def click_on_message(bots_to_respond: List[int], message_args: List[str], message_recieved):
    BANNED_CLICK_WORDS = {
        "в жертву": "Не буду я його різати, мені жаль",
        "Атакувати": "На це буде окрема команда, поки не можу",
        "Купити": "В нас і так ресурсів забагато",
        "Продати": "Лідер/заступ буде - розбереться",
        "Викинути": "Нічого не викидаю, мені все треба",
        "Так": "Паки відкриває мій хазяїн",
        "Совєцкій пайок": "Не треба, ще шизи надає",
        "🟢": "Хуйня баф, воно нам не треба",
        "🟠": "Які рейди на клани? Ми в лізі...",
        "🔴": "Тут хуй п'ять разів на день збираються, раз на 45 хв - то забагато",
        "Перерозподіл": "З паків гроші налутаєш",
        "БПЛА": "Щоб що мені БПЛА?",
        "🟣": "Потім подивлюсь",
        "Змінити квести": "Якби в мене був мозок, щоб знати, чи хороші це квести, я б може й змінив",
    }
    
    row_index = int(message_args[2]) if len(message_args) >=3 else 1
    col_index = int(message_args[3]) if len(message_args) >=4 else 1
    
    original_message = await message_recieved.get_reply_message()
    if original_message.reply_markup is not None and hasattr(original_message.reply_markup, 'rows'):
        for client_index in bots_to_respond:
            for i_row, row in enumerate(original_message.reply_markup.rows, start=1):
                if i_row != row_index:
                    continue
                for j_col, button in enumerate(row.buttons, start=1):
                    if j_col != col_index:
                        continue
                    for key, val in BANNED_CLICK_WORDS.items():
                        if key in button.text:
                            await clients_array[client_index].send_message(message_recieved.chat_id, val, reply_to=message_recieved.id)
                            return
                    try:
                        await clients_array[client_index](GetBotCallbackAnswerRequest(
                            original_message.chat_id,
                            original_message.id,
                            data=button.data
                        ))
                    except:
                        pass