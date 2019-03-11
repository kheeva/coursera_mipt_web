import requests
import datetime


ACCESS_TOKEN = '17da724517da724517da72458517b8abce117da17da72454d235c274f1a2be5f45ee711'


def fetch_uid(username, token):
    url = 'https://api.vk.com/method/users.get'
    params = {
        'v': '5.71',
        'access_token': token,
        'user_ids': username,
        'fields': 'bdate',
    }
    return requests.get(url, params=params).json()['response'][0]['id']


def fetch_user_list(uid, token):
    url = 'https://api.vk.com/method/friends.get'
    params = {
        'v': '5.71',
        'access_token': token,
        'user_id': uid,
        'fields': 'bdate',
    }
    return requests.get(url, params=params).json()['response']['items']


def calc_age(uid):
    user_id = fetch_uid(uid, ACCESS_TOKEN)
    friends_list = fetch_user_list(user_id, ACCESS_TOKEN)
    ages_dict = {}

    for friend in friends_list:
        if not friend.get('bdate') or friend['bdate'].count('.') != 2:
            continue

        birth_year = int(friend['bdate'].split('.')[-1])
        friend_age = datetime.datetime.now().year - birth_year
        ages_dict[friend_age] = ages_dict.get(friend_age, 0) + 1

    ages_list = []

    for age in ages_dict:
        ages_list.append((age, ages_dict[age]))

    return sorted(
        sorted(ages_list, key=lambda x: x[0]),
        key=lambda x: x[1],
        reverse=True
    )


if __name__ == '__main__':
    res = calc_age('reigning')

    print(res)
