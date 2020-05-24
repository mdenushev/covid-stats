import requests
import socket

from objects import CountryRates, CountryIsolation

base_link = 'https://yandex.ru/maps/api/covid'


def get_host_ip():
    host_name = socket.gethostname()
    return socket.gethostbyname(host_name)


class YandexCOVIDAPI:
    def __init__(self):
        self.csrf = str()
        self.cookie_jar = dict()
        self.__update_csrf()

    def __update_csrf(self):
        res = requests.get(base_link, params={'ajax': 1, 'lang': 'ru'})
        self.csrf = res.json()['csrfToken']
        self.cookie_jar.update({cookie.name: cookie.value for cookie in res.cookies})

    def get_isolation_rates(self):
        res = requests.get(base_link, params={'ajax': 1, 'lang': 'ru', 'isolation': 'true', 'csrfToken': self.csrf},
                           headers=self.__get_headers_for_request())

        data = res.json()
        if 'data' not in list(data.keys()):
            self.__update_csrf()
            return self.get_isolation_rates()
        else:
            return [CountryIsolation(country) for country in data['data']['cities']]

    def __get_headers_for_request(self):
        return {'Host': 'yandex.ru',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:71.0) Gecko/20100101 Firefox/71.0',
                'Cookie': self.__cookie_to_str()}

    def __cookie_to_str(self):
        cookie_names = self.cookie_jar.keys()
        return '; '.join([f'{name}={self.cookie_jar[name]}' for name in cookie_names])

    def get_covid_rates(self):
        res = requests.get(base_link, params={'ajax': 1, 'lang': 'ru', 'csrfToken': self.csrf},
                           headers=self.__get_headers_for_request())

        data = res.json()
        if 'data' not in list(data.keys()):
            self.__update_csrf()
            return self.get_covid_rates()
        else:
            return [CountryRates(country) for country in data['data']['items']]

    def get_covid_rates_by_name(self, name):
        objects = self.get_covid_rates()
        for obj in objects:
            if obj.name == name:
                return obj
        return None

    def get_isolation_rates_by_name(self, name) -> CountryIsolation:
        objects = self.get_isolation_rates()
        for obj in objects:
            if obj.name == name:
                return obj
        return None
