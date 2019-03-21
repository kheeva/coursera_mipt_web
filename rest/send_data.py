import requests


uri = 'http://79.137.175.13/'
post_url = 'http://79.137.175.13/submissions/1/'
login = 'alladin'
password = 'opensesame'


def post_request(url, login, password, data=None):
    r = requests.post(url, data=data, auth=requests.auth.HTTPBasicAuth(login, password))
    return r.json()


def put_request(url, login, password, data=None):
    r = requests.put(url, data=data, auth=requests.auth.HTTPBasicAuth(login, password))
    return r.json()


step1 = post_request(post_url, login, password)
print(step1)
step2 = put_request(uri+step1['path'], step1['login'], step1['password'])

with open('answer.txt', 'w') as f:
    f.write(step2['answer'])


