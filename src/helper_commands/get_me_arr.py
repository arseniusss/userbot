import asyncio
from ..constants_imports.imports import clients_array


ME_ARR = []
async def get_me_arr(clients_array):
    global ME_ARR
    tasks = [client.get_me() for client in clients_array]
    me_arr = await asyncio.gather(*tasks)
    ME_ARR = me_arr
    return me_arr

get_me_arr(clients_array)