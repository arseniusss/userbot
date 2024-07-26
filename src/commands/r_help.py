from ..constants_imports.imports import clients_array


async def send_help_message(client_index: int, chat_id: int, message_id: int) -> None:
    message_to_send = '''**Меню команд**
    \n🌐Команди, які не потребують зазначення індекса бота🌐:
    •`.status` - список ботів з назвами та індексами, увімкнені позначені зеленим;
    •`.chats` - список чатів, звідки боти кличуть гумконвої;
    •`.guards` - статус доступності гумконвоїв (зелене - доступний);
    •`.info` - поточні активності чату з посиланнями;
    •`.тривога` - тривога (кривий код, фіксити не хочу);
    •`.raid` - останній рейд цього чату;
    \n**👉Як звернутись до ботів?👈**
    Усі команди починаються з префікса - . Після цього можна зазначити:
    •одне число (приклад .1 команда) - єдиний бот;
    •два числа через - тире (приклад: .2-6) - всі з проміжку від 1-го до 2-го числа;
    •числа,через,кому (приклад: .1,4,9) - всі перелічені боти;
    •.cl (приклад: .cl хп) - всі боти клану;         
    •.all (приклад: .all бд) - всі боти одразу;
    \n📋**Перелік команд📋**
    •клік/тиць/. (приклад: .1 клік) - тикнути на кнопку. Приклад: `.2 клік 3 4` - клікне на 4-ту кнопку 3-го ряду. 3 і 4 - небов'язкові аргументи. Якщо не вказати 3, шукатиме 1 кнопку в 1 ряді, якщо не вказати 4 - шукатиме 1 кнопку в 3 ряді;
    •rusak/русак/r (приклад: .all r) - обрані русаки та їх стати;
    •account/acc/a (приклад: .all a) - аккаунти русаків;
    •status/s/статус/с (приклад: .cl s) - статус аккаунтів (від рандомбота);
    •inventory/інвентар/inv/інв/i/і (приклад: .all i) - поточне вдягнуте на русаків спорядження;
    •class (приклад: .1-3 class) - класи всіх русаків;
    •бд (приклад: .1 бд) - закупити бойовий дух (5 пляшок горілки);
    •хп (приклад: .cl хп) - закупити хп (одна аптечка);
    •guard (приклад: .9-10 guard) - покликати гумконвой. Само перевірить, чи обраний генерал;
    •дуель/duel/d/д к-ть_дуелей (приклад: .1 d 5) - дуелі рандомбота, кине 1 за замовчуванням;
    •tour/турнір/t/т к-ть_турнірів (приклад: .3 t 8) - турніри раддомбота, кине 1 за замовчуванням;
    •/інші_команди (команди рандомбота) можна відправити одразу після /. Приклад: (.1 /i);
    \n🔍**Фільтри🔍**
    Щоб змінити фільтр, треба надіслати: .1 (назва фільтра) on/off/нічого. Якщо нічого не вказати, то зміниться з true на false і навпаки.
    •war - автозахід в міжчати;
    •start_war - автоматичний старт міжчатів;
    •battle - автозахід в битви;
    •start_battle - автоматичний старт масових битв;
    •raid - автозахід в рейд;
    •start_raid - автоматичний старт рейдів;
    •loot - автоматична крадіжка луту(має поставити + після крадіжки);
    •battle_sleep - затримка перед тим, як зайти в битву (приклад: .3 battle_sleep 0.5);
    •makima_mode - дозволити боту автоматично заходити в рейд після того, як пустять гумконвой (приклад: .1 makima_mode on);
    •convoys_limit - після якого числа пущених конвоїв бот зайде в рейд (приклад: .1 convoys_limit 2);
    •horilka - автоматична закупівля горілки перед міжчатом;
    •clan_heal - автохіл клану, коли стається якась хуйня (-100 хп);
    •war_sleep - затримка перед тим, як заходити в міжчат (приклад: .4 war_sleep 0.5);
    '''
    
    await clients_array[client_index].send_message(chat_id, message_to_send, reply_to=message_id, parse_mode="md")