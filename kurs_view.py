import requests

API_KEY = ""
url=f"https://v6.exchangerate-api.com/v6/{API_KEY}/pair/USD/UZS"

response = requests.get(url)
json_data = response.json()
kurs = json_data['conversion_rate']
print(kurs)
