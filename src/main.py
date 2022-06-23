import os
from datetime import datetime

import pytz
import requests
from dateutil import parser
from dotenv import load_dotenv

from src.messenger import send_message


def run(event, context):
    load_dotenv()
    login = str(os.getenv("LOGIN"))
    password = str(os.getenv("PASS"))
    debug = os.getenv("DEBUG", "false") in ["true", "True", "TRUE", True]

    login_url = "https://api.amigoapp.com.br/api/authenticate"
    res = requests.post(login_url,json={
        "email":login,
        "password":password
    })

    if debug:
        print("login res:", res.json())

    login_token = res.json().get("token")
    user_id = res.json().get("user").get("config_agenda_users")[1:-1]


    reference_date = datetime.now().strftime('%Y-%m-%d')

    get_agenda_url = f"https://api.amigoapp.com.br/api/attendance/agenda?end_date={reference_date}&is_view_all_doctors=false&new_listing=true&start_date={reference_date}&user_id={user_id}"

    if debug:
        print("get_agenda_url:", get_agenda_url)
    res = requests.get(get_agenda_url, headers={
        "authorization": f"Bearer {login_token}",
        "company-id": "3546",
        "referer": "https://amigoapp.com.br/"
    })

    agenda_res = res.json()

    if debug:
        print("agenda_res:", agenda_res)

    agenda_res_data = agenda_res.get("data")

    entries = []

    def sort_func(item):
        return parser.parse(item.get("start_date"))

    agenda_res_data.sort(key=sort_func)


    for entry in agenda_res_data:
        reference_date = entry.get("start_date")
        end_date = entry.get("end_date")
        localFormat = "%Y-%m-%dT%H:%M:%S"

        reference_date = datetime.strptime(reference_date[:-5],localFormat).replace(tzinfo=pytz.utc).astimezone(pytz.timezone('America/Sao_Paulo')).strftime('%H:%M')
        end_date = datetime.strptime(end_date[:-5],localFormat).replace(tzinfo=pytz.utc).astimezone(pytz.timezone('America/Sao_Paulo')).strftime('%H:%M')

        schedule_time = f"{reference_date} - {end_date}"
        entries.append({
            "name": entry.get("patient").get("name"),
            "time": schedule_time
        })
        

    if len(entries) > 0:
        msg = "Bom dia! Os pacientes agendados para hoje são:\n"
        for entry in entries:
            name = entry.get('name')
            schedule_time = entry.get('time')
            msg = msg + f'- *{name}* - Horário: {schedule_time} \n'
        send_message(msg)