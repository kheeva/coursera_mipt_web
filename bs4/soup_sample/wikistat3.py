import re
import os
import time

import lxml
from bs4 import BeautifulSoup
from collections import deque


# Вспомогательная функция, её наличие не обязательно и не будет проверяться
def build_tree(start, end, path):
    files = dict.fromkeys(os.listdir(path))
    files_set = set([''.join(['/wiki/', f]) for f in files.keys()])
    tree = []

    parsed_links = set()
    links_to_parse = deque()
    links_to_parse.append([start])

    def get_downlinks(link, path='./wiki/'):
        with open("{}{}".format(path, link)) as html:
            soup = BeautifulSoup(html, 'lxml')

        div = soup.find('div', {'id': 'bodyContent'})
        links = div.find_all('a', href=True)
        links_set = set([l['href'] for l in links])
        _downlinks = [d[6:] for d in files_set & links_set]
        return _downlinks

    while links_to_parse:
        branch = []
        step_link_to_parse = links_to_parse.popleft()

        if end in step_link_to_parse:
            tree.append([end])
            return tree

        tree.append(step_link_to_parse)

        for link in step_link_to_parse:
            if link not in parsed_links:
                branch += get_downlinks(link)
                parsed_links.add(link)

        if branch:
            links_to_parse.append(branch)

    return tree


# Вспомогательная функция, её наличие не обязательно и не будет проверяться
def build_bridge(start, end, path):
    files = build_tree(start, end, path)
    bridge = []
    # TODO Добавить нужные страницы в bridge
    bridge.append(end)
    for link in files['end']:
        pass
    return bridge


def parse(start, end, path):
    """
    Если не получается найти список страниц bridge, через ссылки на которых можно добраться от start до end, то,
    по крайней мере, известны сами start и end, и можно распарсить хотя бы их: bridge = [end, start]. Оценка за тест,
    в этом случае, будет сильно снижена, но на минимальный проходной балл наберется, и тест будет пройден.
    Чтобы получить максимальный балл, придется искать все страницы. Удачи!
    """

    bridge = build_bridge(start, end, path)  # Искать список страниц можно как угодно, даже так: bridge = [end, start]

    # Когда есть список страниц, из них нужно вытащить данные и вернуть их
    out = {}
    for file in bridge:
        with open("{}{}".format(path, file)) as data:
            soup = BeautifulSoup(data, "lxml")

        body = soup.find(id="bodyContent")

        # TODO посчитать реальные значения
        imgs = 5  # Количество картинок (img) с шириной (width) не меньше 200
        headers = 10  # Количество заголовков, первая буква текста внутри которого: E, T или C
        linkslen = 15  # Длина максимальной последовательности ссылок, между которыми нет других тегов
        lists = 20  # Количество списков, не вложенных в другие списки

        out[file] = [imgs, headers, linkslen, lists]

    return out

start = 'Stone_Age'
end = 'Python_(programming_language)'
path = './wiki/'

t = time.time()
f = build_tree(start, end, path)
for i in f:
    print(i)
print(time.time() - t)
