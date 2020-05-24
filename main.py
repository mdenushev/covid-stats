from datetime import datetime
import numpy as np
from api import YandexCOVIDAPI
import matplotlib.pyplot as plt

yndx = YandexCOVIDAPI()


def show_plot(region: str, city: str):
    rates = yndx.get_covid_rates_by_name(region)
    isolation = yndx.get_isolation_rates_by_name(city)
    time = []
    cases = []
    isolation_rate = []

    isolation_rates_dict = {datetime.fromtimestamp(history['ts']).strftime('%d-%m'): float(history['value']) for history
                            in
                            isolation.history_day}
    last = 0
    for history in rates.histogram:
        date = datetime.fromtimestamp(history['ts']).strftime('%d-%m')
        time.append(date)
        difference = history['value'] - last
        cases.append(float(difference))
        if difference > 0:
            last += difference

    last = 0
    isolation_rate.append(0)
    for day in time:
        if day in isolation_rates_dict:
            isolation_rate.append(5 - isolation_rates_dict[day])
            last = 5 - isolation_rates_dict[day]
        else:
            isolation_rate.append(last)
    isolation_rate[0] = isolation_rate[1]
    isolation_rate.pop()
    fig, ax1 = plt.subplots()

    ax1.bar(time, cases, label='Новые случаи заражения')
    ax1.plot(np.nan, '.-', color='tab:red', label='Индекс количества людей на улице (выше - больше)')
    ax1.set_xlabel('Дата')
    ax1.set_ylabel('Новые случаи заражения')
    ax1.legend(loc=0)
    ax1.tick_params(labelrotation=90)

    ax2 = ax1.twinx()
    ax2.plot(time, np.array(isolation_rate), '.-', color='tab:red', label='Индекс количества людей на улице')
    ax2.set_ylim(0, 5)
    ax2.set_ylabel('Индекс количества людей на улице')

    plot_title = f'{city} - {rates.cases} / {rates.cured} / {rates.deaths}'
    plt.title(plot_title)
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    plt.grid(axis='both')
    plt.show()


if __name__ == '__main__':
    cities = [
        {'region': 'Томская область', 'city': 'Томск'},
        {'region': 'Кемеровская область', 'city': 'Кемерово'},
        {'region': 'Новосибирская область', 'city': 'Новосибирск'}
    ]
    for city_info in cities:
        show_plot(city_info['region'], city_info['city'])
