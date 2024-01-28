import emoji
import re


def emoji_loot_map(text: str) -> dict[str, int]:
    # TODO: спробувати переробити ці методи в 1
    emojis = list(emoji.emoji_list(text[text.find('\n'):]))
    emoji_list =  [e['emoji'] for e in emojis]
    map_of_emoji_loot = {}
    clan_resources = ['🌳', '🪨', '🧶', '🧱', '👾', '🪙', '🤖', '🟡']
    for my_emoji in emoji_list:
        text = text[text.find(my_emoji):]
        if not my_emoji in clan_resources:
            if my_emoji == '🍉':
                map_of_emoji_loot['🍉'] = 1
            else:
                match = re.search(r'[+-]?\d+', text)
                if match:
                    if my_emoji != '🍉':
                        map_of_emoji_loot[my_emoji] = int(match.group())
    if len(map_of_emoji_loot.keys()) == 0:
        map_of_emoji_loot = {
            'нічого корисного': ""
        }

    return map_of_emoji_loot


RUSAK_CLASSES_EMOJI = ["🤙","🧰","🔮","🗿","🪖","👮","🤡","📟","⛑","🚬","🚕","🎖",]

def rusak_stats_map(text: str) -> dict[str, int]:
    emojis = list(emoji.emoji_list(text))
    emoji_list =  [e['emoji'] for e in emojis]
    rusak_stats = {}
    for my_emoji in emoji_list:
        text = text[text.find(my_emoji):]
        if not (my_emoji in RUSAK_CLASSES_EMOJI) and my_emoji != "🏷" and my_emoji != '🐒':
            match = re.search(r'\d+', text)
            if match:
                rusak_stats[my_emoji] = int(match.group())

    return rusak_stats