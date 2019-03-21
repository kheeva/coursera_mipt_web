import requests


url_1 = 'http://127.0.0.1:8000/api/v1/goods/'
url_2 = 'http://127.0.0.1:8000/api/v1/goods/2/reviews/'
url_3 = 'http://127.0.0.1:8000/api/v1/goods/3/'
request_1 = {
  "title": "Сыр \"Российский\"",
  "description": "Очень вкусный сыр, да еще и российский.",
  "price": 100
}
request_2 = {
  "text": "Best. Cheese. Ever.",
  "grade": 10
}

# r = requests.post(url_1, json=request_1)
r = requests.get(url_3)
print(r, r.content)
