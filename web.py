import os

from flask import Flask, request, send_file, render_template
from flask_request_validator import (
    GET,
    Param,
    Pattern,
    validate_params
)

from ploter import make_archive

app = Flask(__name__)


@app.route('/stats', methods=['GET'])
@validate_params(
    Param('regions', GET, str, rules=[Pattern(r'([а-яА-Я\- ()]+,?)')], default=''),
    Param('cities', GET, str, rules=[Pattern(r'([а-яА-Я\- ()]+,?)')], default='', required=False),
    Param('announcement', GET, bool, default=True, required=False)
)
def stats_route(regions, cities, announcement):
    regions = regions.split(',')
    cities = cities.split(',')

    archive = make_archive(regions, cities, announcement, True, True)

    return send_file(archive)


@app.route('/', methods=['GET'])
def index_page():
    return open('templates/index.html', encoding='utf-8').read()


if __name__ == '__main__':
    if not os.path.exists('data'):
        os.makedirs('data')
    app.run('0.0.0.0', 3003)
