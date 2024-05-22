from fastapi import FastAPI, HTTPException
import requests
import json

app = FastAPI()

SERVER_URL = "http://your_1c_server_address:port"

@app.get("/get_data_from_1c")
def get_data_from_1c():
    api_url = f"{SERVER_URL}/api/data"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))


API_ROUTE = "/api/send_data_to_1c"
with open('cities.json', 'r', encoding='utf-8') as f:
    cities_from_db = json.load(f)
try:
    response = requests.post(f"{SERVER_URL}{API_ROUTE}", json=cities_from_db)
    response.raise_for_status()
    print("Данные успешно отправлены на сервер 1C.")
    print("Ответ сервера 1C:")
    print(response.json())
except requests.exceptions.RequestException as e:
    print("Произошла ошибка при отправке данных на сервер 1C:", str(e))
