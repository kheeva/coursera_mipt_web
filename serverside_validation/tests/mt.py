import requests


url_1 = 'http://127.0.0.1:8000/api/v1/goods/'
url_2 = 'http://127.0.0.1:8000/api/v1/goods/3/reviews/'
url_3 = 'http://127.0.0.1:8000/api/v1/goods/4/'
request_1 = {
  "title": "Сыр \"Российский\"",
  "description": "Очень вкусный сыр, да еще и российский.",
  "price": 100
}
request_2 = {
  "text": "Best. Cheese. Ever.",
  "grade": 10
}


def post_request(url, login, password, data=None, json=None):
  r = requests.post(url, data=data, json=json,
                    auth=requests.auth.HTTPBasicAuth(login, password))

  print(r, r.content)


def get_request(url, login, password, data=None):
  r = requests.get(url, params=data,
                   auth=requests.auth.HTTPBasicAuth(login, password))
  # return r.json()
  print(r, r.content)


# r = requests.post(url_2, json=request_2)
# r = requests.get(url_3)
print(post_request(url_2, 'kheeva', '123123k', json=request_2))

# url_x = 'http://127.0.0.1:8000/api/v1/goods/3/'
# print(get_request(url_x, 'kheeva', '123123k'))








# class AuthenticatedStaffMixin(AccessMixin):
#   """Verify that the current user is authenticated and staff"""
#
#   def dispatch(self, request, *args, **kwargs):
#     if 'HTTP_AUTHORIZATION' in request.META:
#       auth_data = request.META['HTTP_AUTHORIZATION'].split()
#       if len(auth_data) == 2:
#         if auth_data[0].lower() == 'basic':
#           username, password = base64.b64decode(auth_data[1]).decode(
#             'ascii').split(':')
#           user = authenticate(request, username=username, password=password)
#
#           if user is not None and user.is_active:
#             if not user.is_staff:
#               return HttpResponse('', status=403)
#
#             return super().dispatch(request, *args, **kwargs)
#
#     return HttpResponse('', status=401)