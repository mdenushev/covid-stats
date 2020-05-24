class CountryRates:
    def __init__(self, data: dict):
        self.name = data['name']
        self.cases = data['cases']
        self.cured = data['cured']
        self.deaths = data['deaths']
        self.histogram = data['histogram'] if 'histogram' in data else []
        self.ru = data['ru'] if 'ru' in data else False


class CountryIsolation:
    def __init__(self, data: dict):
        self.name = data['name']
        self.population = data['population']
        self.history_day = data['histogramDays']
        self.history_hours = data['histogramHours']
        self.ru = data['ru'] if 'ru' in data else False
