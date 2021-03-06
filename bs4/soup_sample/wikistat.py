import re
import os

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

        body = soup.find('div', {'id': 'bodyContent'})

        # TODO посчитать реальные значения
        # imgs = 5  # Количество картинок (img) с шириной (width) не меньше 200
        # headers = 10  # Количество заголовков, первая буква текста внутри которого: E, T или C
        # linkslen = 15  # Длина максимальной последовательности ссылок, между которыми нет других тегов
        # lists = 20  # Количество списков, не вложенных в другие списки

        # 1. count images whose width >= 200
        images_count = 0
        for pic in body.find_all('img', width=True):
            if int(pic['width']) >= 200:
                images_count += 1

        # 2. count headers starts with [ETC]
        headers = 0
        for h_tag in body.select("h1, h2, h3, h4, h5, h6"):
            if re.match(r'^[ETC].*$', h_tag.text):
                headers += 1

        # 3. calc length of sequence of links at the same level
        max_links_seq_len = 0
        next_link = body.find_next('a')
        while next_link:
            level_links_seq_len = 1
            for sibling in next_link.find_next_siblings():
                if sibling.name != 'a':
                    break
                level_links_seq_len += 1

            max_links_seq_len = max(level_links_seq_len, max_links_seq_len)
            next_link = next_link.find_next('a')

        # 4. count html lists not inserted in other html lists
        html_lists_count = 0
        html_lists = body.find_all(['ul', 'ol'])
        for html_list in html_lists:
            if not html_list.find_parents(['ul', 'ol']):
                html_lists_count += 1

        out[file] = [images_count, headers, max_links_seq_len, html_lists_count]

    return out
