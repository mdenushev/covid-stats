import os
import shutil
import uuid
import zipfile
from threading import Thread

from api import YandexCOVIDAPI
import datetime
import matplotlib.pyplot as plt

announcements = ['25-03', '08-04', '28-04', '11-05']
yandex_api = YandexCOVIDAPI()
base_folder = 'data'


def insert_announcements(ax: plt.Axes):
    for i in range(len(announcements)):
        ax.axvline(announcements[i], color='tab:grey', label='Обращение Путина' if i == 0 else '', linestyle='--')


def format_name(region: str) -> str:
    return region.replace(' ', '_')


def get_date_ticks(dates: [str], max_len: int = 10) -> [str]:
    return [dates[i] for i in range(0, len(dates), int(len(dates) / max_len))]


def make_plot(data, dates, label, title, color, show_announcement=True):
    figure, plot = plt.subplots(constrained_layout=True)

    plot.plot(dates, data, label=label, color=color)
    if show_announcement:
        insert_announcements(plot)

    plot.set_xlabel('Дата')
    plot.set_xticks(get_date_ticks(dates, 10))
    plot.set_ylabel(label)
    # plt.legend(loc=0)
    plot.tick_params(labelrotation=30)
    figure.suptitle(title, fontsize=16)
    plt.tight_layout()

    return figure


def cases_plot_by_region(region: str, show_announcement: bool = True, color: str = '#0000FF',
                         folder: str = 'data') -> str:
    """
    Returns plot filename
    :param folder: Folder to save file
    :param color: Color hex for plot
    :param show_announcement:
    :param region: City name (using yandex)
    :return: Filename
    """
    data = yandex_api.get_covid_rates_by_name(region)
    if data is None:
        return ''
    # Calculate fact death ratio
    death_rate = round((data.deaths / (data.cured + data.deaths)) * 100, 2)
    dates = [datetime.datetime.fromtimestamp(date['ts']).strftime('%d-%m') for date in data.histogram]
    cases = [date['value'] for date in data.histogram]

    plot_title = f'{region} {data.cases}/{data.cured}/{data.deaths} ({death_rate}%)'
    figure = make_plot(cases, dates, 'Число зараженных', plot_title, color, show_announcement=show_announcement)

    filename = f'{folder}/{datetime.datetime.now().isoformat()}_{format_name(region)}_all_cases.png'
    figure.savefig(filename)

    return filename


def new_cases_plot_by_region(region: str, show_announcement: bool = True, color: str = '#8b00ff',
                             folder: str = 'data'):
    rates = yandex_api.get_covid_rates_by_name(region)
    if rates is None:
        return ''
    dates = []
    cases = []

    last = 0
    for history in rates.histogram:
        date = datetime.datetime.fromtimestamp(history['ts']).strftime('%d-%m')
        dates.append(date)
        difference = history['value'] - last
        cases.append(float(difference))
        if difference > 0:
            last += difference
    plot_title = f'{region} - Новые случаи'
    figure = make_plot(cases, dates, 'Новые случаи', plot_title, color, show_announcement=show_announcement)

    filename = f'{folder}/{datetime.datetime.now().isoformat()}_{format_name(region)}_new_cases.png'
    figure.savefig(filename)

    return filename


def isolation_plot_by_city(city: str, show_announcement: bool = True, color: str = '#FF0000',
                           folder: str = 'data'):
    isolation = yandex_api.get_isolation_rates_by_name(city)
    if isolation is None:
        return ''
    dates = []
    isolation_rate = []

    for rate in isolation.history_day:
        dates.append(datetime.datetime.fromtimestamp(rate['ts']).strftime('%d-%m'))
        isolation_rate.append(float(rate['value']))

    plot_title = f'{city} - Индекс самоизоляции (Яндекс)'
    figure = make_plot(isolation_rate, dates, 'Индекс самоизоляции (Яндекс)', plot_title, color,
                       show_announcement=show_announcement)

    filename = f'{folder}/{datetime.datetime.now().isoformat()}_{format_name(city)}_isolation.png'
    figure.savefig(filename)

    return filename


def make_archive(regions: [str], cities: [str], show_announcement: bool, cases: bool, new_cases: bool) -> str:
    req_id = str(uuid.uuid4())
    folder = base_folder + f'/{req_id}'
    file_name = base_folder + f'/{req_id}.zip'
    os.mkdir(folder)
    threads = list()

    for region in regions:
        if cases:
            x = Thread(target=cases_plot_by_region, args=(region, show_announcement), kwargs={'folder': folder})
            threads.append(x)
            x.start()
        if new_cases:
            x = Thread(target=new_cases_plot_by_region, args=(region, show_announcement), kwargs={'folder': folder})
            threads.append(x)
            x.start()

    for city in cities:
        x = Thread(target=isolation_plot_by_city, args=(city, show_announcement), kwargs={'folder': folder})
        threads.append(x)
        x.start()

    for th in threads:
        th.join()

    zipf = zipfile.ZipFile(file_name, 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(folder):
        for file in files:
            zipf.write(os.path.join(root, file), arcname=file)
    zipf.close()
    shutil.rmtree(folder)
    return file_name


if __name__ == '__main__':
    start = datetime.datetime.now()
    arch = make_archive(
        ['Томская область', 'Кемеровская область', 'Новосибирская область', 'Москва', 'Краснодарский край'],
        ['Томск', 'Кемерово', 'Новосибирск', 'Москва', 'Краснодар'],
        True, True, True
    )
    elapsed = datetime.datetime.now() - start
    print(f'Archive saved at {arch}. Time: {str(elapsed)}')
