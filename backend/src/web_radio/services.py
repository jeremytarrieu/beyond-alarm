import json
from aiohttp import ClientSession

def get_saved_radios():
    with open('../app_data/web_radio/web_radio.json') as file:
        web_radios = json.loads(file.read())
        return web_radios

async def search_radios(query: str):
    async with ClientSession() as session:
        pass
