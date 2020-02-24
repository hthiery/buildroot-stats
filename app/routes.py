import json

from collections import OrderedDict
from flask import (abort, render_template, redirect, request, url_for)
from os import (listdir, getcwd)
from os.path import (isfile, join)

from app import app

from .gravatar import (get_gravatars, get_gravatar_link)


def _get_data():
    data = None

    try:
        with open('data/latest.json') as json_file:
            data = json.load(json_file)
    except AttributeError:
        abort(404, description="Resource not found")

    return data


def _get_stats():
    files = [f for f in listdir('data/stats') if isfile(join('data/stats', f))]
    files = sorted(files)

    stats = {}

    for f in files:
        with open('data/stats/'+f) as json_file:

            d = json.load(json_file)

            if 'labels' not in stats:
                stats['labels'] = []
            stats['labels'].append(str(d['date'][:10]))

            for k, v in d['stats'].items():
                if k in 'infras':
                    continue
                if k not in stats:
                    stats[k] = []
                if k not in d['stats']:
                    stats[k].append(None)
                else:
                    stats[k].append(d['stats'][k])

    return stats


@app.errorhandler(404)
def page_not_found(msg):
    print(msg)
    return render_template('404.html', msg=msg, commit=''), 404


@app.route('/')
def index():
    return redirect('packages')


@app.route('/packages', methods=['GET'])
def packages():
    data = _get_data()
    packages = {}

    developer = request.args.get('developer')
    status = request.args.get('status')
    infra = request.args.get('filter')

    if developer is not None:
        for pkg_name in data['packages']:
            for dev in data['packages'][pkg_name]['developers']:
                if dev == developer:
                    packages[pkg_name] = (data['packages'][pkg_name])
        title = u'{} packages maintained by {}'.format(len(packages), developer)

    elif status is not None:
        for pkg_name in data['packages']:
            pkg = data['packages'][pkg_name]
            if pkg['status'][status][0] != 'ok':
                packages[pkg_name] = pkg
        title = u'{} packages with error in {}'.format(len(packages), status)

    elif infra is not None:
        for pkg_name in data['packages']:
            pkg = data['packages'][pkg_name]
            if pkg['infras']:
                if pkg['infras'][0][1] == infra:
                    packages[pkg_name] = pkg
        title = u'{} packages with {} infrastructure'.format(len(packages), infra)
    else:
        packages = data['packages']
        title = u'Total amount of packages: {}'.format(len(packages))

    packages = OrderedDict(sorted(packages.items(), key=lambda t: t[0]))

    return render_template('packages.html',
                           title=title,
                           packages=packages,
                           status_checks=data['package_status_checks'],
                           commit=data['commit'])


@app.route('/package/<name>')
def package(name):
    data = _get_data()

    pkg = data['packages'][name]
    keys = pkg.keys()

    gravatars = get_gravatars(pkg['developers'], size=50)

    return render_template('package.html',
                           name=name, pkg=pkg,
                           gravatars=gravatars,
                           status_checks=data['package_status_checks'],
                           commit=data['commit'])


@app.route('/developers')
def developers():
    data = _get_data()
    developers = {}

    for pkg_name in data['packages']:
        for developer in data['packages'][pkg_name]['developers']:
            if developer not in developers:
                developers[developer] = {'pkg_count': 0, 'defconfig_count': 0}
            developers[developer]['pkg_count'] += 1

    for defconfig_name in data['defconfigs']:
        for developer in data['defconfigs'][defconfig_name]['developers']:
            if developer not in developers:
                developers[developer] = {'pkg_count': 0, 'defconfig_count': 0}
            developers[developer]['defconfig_count'] += 1

    developers = OrderedDict(sorted(developers.items(), key=lambda t: t[0]))
    gravatars = get_gravatars(developers, size=30)

    title = u'Total amount of developers: {}'.format(len(developers))

    return render_template('developers.html',
                           title=title,
                           developers=developers,
                           gravatars=gravatars,
                           status_checks=data['package_status_checks'],
                           commit=data['commit'])


@app.route('/defconfigs')
def defconfigs():
    data = None
    data = _get_data()

    defconfigs = packages = {}

    defconfigs= OrderedDict(sorted(data['defconfigs'].items(), key=lambda t: t[0]))

    title = u'Total amount of defconfigs: {}'.format(len(defconfigs))

    return render_template('defconfigs.html',
                           title=title,
                           defconfigs=defconfigs,
                           status_checks=data['package_status_checks'],
                           commit=data['commit'])


@app.route('/stats')
def stats():
    data = None
    stats = None

    data = _get_data()
    stats = _get_stats()

    return render_template('stats.html',
                           stats=stats,
                           status_checks=data['package_status_checks'],
                           commit=data['commit'])


@app.route('/json')
def json_stats():
    # add a symlink to data/latest.json into static/lastest.json
    return redirect(url_for('static', filename = 'latest.json'))
