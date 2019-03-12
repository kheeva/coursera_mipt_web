import re
import os
import time

from bs4 import BeautifulSoup
from collections import deque


# Вспомогательная функция, её наличие не обязательно и не будет проверяться
def build_links_path(start, end, path):
    files = dict.fromkeys(os.listdir(path))
    files_set = set([''.join(['/wiki/', f]) for f in files.keys()])

    def get_downlinks(link, path='./wiki/'):
        with open("{}{}".format(path, link)) as html:
            soup = BeautifulSoup(html, 'lxml')

        div = soup.find('div', {'id': 'bodyContent'})
        links = div.find_all('a', href=True)
        links_set = set([l['href'] for l in links])
        _downlinks = [d[6:] for d in files_set & links_set]
        return _downlinks

    parsed_links = set()
    links_to_parse = deque()
    links_to_parse.append([([start], []),])

    while links_to_parse:
        search_level_links = []
        graph_level_nodes = links_to_parse.popleft()

        for links_data in graph_level_nodes:
            links, graph_path = links_data
            if end in links:
                graph_path.append(end)
                return graph_path

            for link in links:
                if link in parsed_links:
                    continue

                downlinks = get_downlinks(link)
                new_path = graph_path + [link]
                search_level_links.append((
                    downlinks,
                    new_path
                ))
                parsed_links.add(link)

        if search_level_links:
            links_to_parse.append(search_level_links)


def parse(start, end, path):
    """
    Если не получается найти список страниц bridge, через ссылки на которых можно добраться от start до end, то,
    по крайней мере, известны сами start и end, и можно распарсить хотя бы их: bridge = [end, start]. Оценка за тест,
    в этом случае, будет сильно снижена, но на минимальный проходной балл наберется, и тест будет пройден.
    Чтобы получить максимальный балл, придется искать все страницы. Удачи!
    """

    bridge = build_links_path(start, end, path)  # Искать список страниц можно как угодно, даже так: bridge = [end, start]

    # Когда есть список страниц, из них нужно вытащить данные и вернуть их
    out = {}
    for file in bridge:
        with open("{}{}".format(path, file)) as data:
            soup = BeautifulSoup(data, "lxml")

        body = soup.find(id="bodyContent")

        images_count = 0
        for pic in body.find_all('img', width=True):
            if int(pic['width']) >= 200:
                images_count += 1

        headers = 0
        for h_tag in body.select("h1, h2, h3, h4, h5, h6"):
            if re.match(r'^[ETC].*$', h_tag.text):
                headers += 1

        links_seq_len = 0
        max_links_seq_len = 0
        tags = [elem.name for elem in body.find('a').next_elements]

        for tag in tags:
            # print('tag', tag.name)
            if tag == 'a':
                links_seq_len += 1
            elif tag is not None:
                max_links_seq_len = max(links_seq_len, max_links_seq_len)
                links_seq_len = 0

        # TODO посчитать реальные значения
        # imgs = 5  # Количество картинок (img) с шириной (width) не меньше 200
        # headers = 10  # Количество заголовков, первая буква текста внутри которого: E, T или C
        # linkslen = 15  # Длина максимальной последовательности ссылок, между которыми нет других тегов
        # lists = 20  # Количество списков, не вложенных в другие списки

        out[file] = [images_count, headers, max_links_seq_len]

    return out


start = 'Stone_Age'
# start = 'Brain'
end = 'Python_(programming_language)'
path = './wiki/'

# t = time.time()
# x = parse(start, end, path)
# print(x)
# print(time.time() - t)

with open("{}{}".format(path, 'Brain')) as data:
    soup = BeautifulSoup(data, "lxml")

# body = soup.find('div', {'id': 'bodyContent'})
body = soup.find(id="bodyContent")
print(dir(body))

links_seq_len = 0
max_links_seq_len = 0
tags = [elem.name for elem in body.next_elements if elem.name is not None]
print(tags)
print(soup.tagStack)
for tag in tags:
    if tag in ['a',]:
        links_seq_len += 1
    else:
        max_links_seq_len = max(links_seq_len, max_links_seq_len)
        links_seq_len = 0

print(max_links_seq_len)

#
# def lll(file, path):
#     # with open("{}{}".format(path, file)) as data:
#     #     soup = BeautifulSoup(data, "lxml")
#     #
#     # body = soup.find(id="bodyContent")
#
#     regex = r"(?:<a.*?</a>)+[^(<a)]*?(?:<a.*?</a>)+"
#
#     test_str = ("<a href=\"Stone age\">Stone age</a>\n"
#                 "<p>paragraph</p>\n"
#                 "<a href=\"Python\">Python</a> текст <a href=\"C\">C</a>\n"
#                 "<a href=\"Javascript\">Javascript</a>\n"
#                 "<b>text</b><br />\n"
#                 "<a href='Scala'>Scala</a> <a href=\"Scala2\">Scala2</a>")
#
#     # print(type(body.contents))
#     print(re.findall(regex, test_str))

# lll(start, path)
# test_str = ("<a href=\"Stone age\">Stone age</a>\n"
#                 "<p>paragraph</p>\n"
#                 "<a href=\"Python\">Python</a> текст <a href=\"C\">C</a>\n"
#                 "<a href=\"Javascript\">Javascript</a>\n"
#                 "<b>text</b><br />\n"
#                 "<a href='Scala'>Scala</a> <a href=\"Scala2\">Scala2</a>")
#
# b = BeautifulSoup(test_str, 'lxml')


# links_count = 0
# max_sequence = 0
#
# for i in b.body.next_elements:
#     if i.name == 'a':
#         links_count += 1
#         print(i.string, links_count)
#     elif i.name is not None:
#         max_sequence = max(links_count, max_sequence)
#         links_count = 0
#
#
# print(max_sequence)
