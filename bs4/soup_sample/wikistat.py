import re
import os

import lxml
from bs4 import BeautifulSoup



# Вспомогательная функция, её наличие не обязательно и не будет проверяться
def build_tree(start, end, path):
    pages_tree = []
    link_re = re.compile(r"(?<=/wiki/)[\w()]+")  # Искать ссылки можно как угодно, не обязательно через re
    files = dict.fromkeys(os.listdir(path))  # Словарь вида {"filename1": None, "filename2": None, ...}
    # TODO Проставить всем ключам в files правильного родителя в значение, начиная от start
    with open("{}{}".format(path, start)) as html:
        soup = BeautifulSoup(html, 'lxml')
    div = soup.find('div', {'id': 'bodyContent'})
    links = div.find_all('a', href=True)

    # r = [l.text for l in links]
    # if end in r:
    #     return pages_tree
    # else:
    #     print(r)
    #     print(len(r))
    # return files


    # for link in links:
    #     print(link.text)
        # if link.text in files.keys():
        #     files[link.text] = start

    files_set = set([''.join(['/wiki/', f]) for f in files.keys()])
    links_set = set([l['href'] for l in links])
    print(files_set)
    # print(links_set)
    downlinks = [d[6:] for d in files_set & links_set]
    downlinks_to_parse = set()

    for downlink in downlinks:
        if not files[downlink]:
            files[downlink] = [start]
        else:
            files[downlink].append(start)

        if end != downlink:
            downlinks_to_parse.add(downlink)

    for link_to_parse in downlinks_to_parse:
        print(link_to_parse)
        build_tree('/wiki/'+link_to_parse, end, files)

    return files


# Вспомогательная функция, её наличие не обязательно и не будет проверяться
def build_bridge(start, end, path):
    files = build_tree(start, end, path)
    bridge = []
    # TODO Добавить нужные страницы в bridge
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
build_tree(start, end, path)