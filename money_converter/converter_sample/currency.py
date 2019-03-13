from bs4 import BeautifulSoup
from decimal import Decimal


def from_rub(amount, cur_to, soup):
    if cur_to == 'RUR':
        return amount

    value_to = soup.find('CharCode', text=cur_to).find_next_sibling(
        'Value').string
    value_to = Decimal(str(value_to).replace(',', '.'))
    nominal_to = soup.find('CharCode', text=cur_to).find_next_sibling(
        'Nominal').string
    nominal_to = Decimal(str(nominal_to))
    amount = Decimal(amount)
    result = amount / (value_to / nominal_to)
    return result


def to_rub(amount, cur_from, soup):
    if cur_from == 'RUR':
        return amount

    value_from = soup.find('CharCode', text=cur_from).find_next_sibling(
        'Value').string
    value_from = Decimal(str(value_from).replace(',', '.'))
    nominal_from = soup.find('CharCode', text=cur_from).find_next_sibling(
        'Nominal').string
    nominal_from = Decimal(str(nominal_from))
    amount = Decimal(amount)
    result = amount * (value_from / nominal_from)
    return result


def convert(amount, cur_from, cur_to, date, _requests):
    params = {'date_req': date}
    url = 'http://www.cbr.ru/scripts/XML_daily.asp'
    response = _requests.get(url, params=params)
    soup = BeautifulSoup(response.content, 'xml')
    amount_rubles = to_rub(amount, cur_from, soup)
    result = from_rub(amount_rubles, cur_to, soup)
    return Decimal(str(result)).quantize(Decimal('.0001'))
