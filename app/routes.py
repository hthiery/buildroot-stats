import json

from collections import OrderedDict
from flask import render_template, redirect, request
from os import listdir, getcwd
from os.path import isfile, join

from app import app

def _get_data():
    data = None
    with open('data/latest.json') as json_file:
        data = json.load(json_file)
    return data

def _get_stats():
    data = {}
    files = [f for f in listdir('data/stats') if isfile(join('data/stats', f))]
    files = sorted(files)

    stats = {
        'labels': [],
        'packages': [],
        'no-hash': [],
        'version-not-uptodate': [],
    }

    for f in files:
        with open('data/stats/'+f) as json_file:
            d = json.load(json_file)
            stats['labels'].append(str(d['date'][:10]))
            stats['packages'].append(d['stats']['packages'])
            stats['version-not-uptodate'].append(d['stats']['version-not-uptodate'])
            stats['no-hash'].append(d['stats']['no-hash'])

    return stats

@app.route('/')
def index():
    return redirect('packages')

@app.route('/packages', methods=['GET'])
def packages():
    data = _get_data()

    packages = OrderedDict(sorted(data['packages'].items(), key=lambda t: t[0]))

    title = 'Total amount of packages: {}'.format(len(packages))

    return render_template('packages.html',
                           title=title,
                           packages=packages,
                           commit=data['commit'])

@app.route('/package/<name>')
def package(name):
    data = _get_data()

    pkg = data['packages'][name]
    keys = pkg.keys()

    return render_template('package.html',
                           pkg=pkg, keys=keys,
                           commit=data['commit'])

@app.route('/filter/<filter>')
def filter(filter):
    data = _get_data()
    packages = {}

    for pkg_name in data['packages']:
        pkg = data['packages'][pkg_name]
        if pkg['status'][filter][0] != 'ok':
            packages[pkg_name] = pkg
        title = '{} packages with error in {}'.format(len(packages), filter)

    packages = OrderedDict(sorted(packages.items(), key=lambda t: t[0]))

    return render_template('packages.html',
                           title=title,
                           packages=packages,
                           commit=data['commit'])

@app.route('/infrastructure/<infra>')
def infrastructure(infra):
    data = _get_data()
    packages = {}

    for pkg_name in data['packages']:
        pkg = data['packages'][pkg_name]
        if pkg['infras']:
            if pkg['infras'][0][1] == infra:
                packages[pkg_name] = pkg


    packages = OrderedDict(sorted(packages.items(), key=lambda t: t[0]))

    title = '{} packages with {} infrastructure'.format(len(packages), infra)

    return render_template('packages.html',
                           title=title,
                           packages=packages,
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

    return render_template('developers.html',
                           developers=developers,
                           commit=data['commit'])

@app.route('/developer/<developer>')
def developer(developer):
    data = None
    data = _get_data()

    packages = {}
    for pkg_name in data['packages']:
        for dev in data['packages'][pkg_name]['developers']:
            if dev == developer:
                packages[pkg_name] = (data['packages'][pkg_name])

    title = '{} packages maintained by {}'.format(len(packages), developer)

    return render_template('packages.html',
                           title=title,
                           packages=packages,
                           commit=data['commit'])

@app.route('/defconfigs')
def defconfigs():
    data = None
    data = _get_data()

    defconfigs = packages = {}

    defconfigs= OrderedDict(sorted(data['defconfigs'].items(), key=lambda t: t[0]))

    title = '{} defconfigs'.format(len(data['defconfigs']))

    return render_template('defconfigs.html',
                           title=title,
                           defconfigs=defconfigs,
                           commit=data['commit'])

@app.route('/stats')
def stats():
    data = None
    stats = None

    data = _get_data()
    stats = _get_stats()

    print(stats)
    return render_template('stats.html',
                           stats=stats,
                           commit=data['commit'])
