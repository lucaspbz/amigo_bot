import os

import requests

def send_message(msg:str):
    chat_id = str(os.getenv("CHAT_ID"))
    bot_token = str(os.getenv("BOT_TOKEN"))

    requests.get(f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={msg}&parse_mode=markdown")
