import json

from collections import OrderedDict
from flask import (abort, render_template, redirect, request, url_for)
from os import (listdir)
from os.path import (isfile, join)

from app import app

from . import models

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

    # GET
    developer = request.args.get('developer')
    status = request.args.get('status')
    infra = request.args.get('infra')

    if developer is not None:
        records = app.session.query(models.Package).filter(models.Package.developers.any(email=developer)).order_by(models.Package.name.asc()).all()
        title = u'{} package(s) maintained by {}'.format(len(records), developer)
    else:
        records = app.session.query(models.Package).order_by(models.Package.name.asc()).all()
        title = u'Total amount of packages: {}'.format(len(records))

    return render_template('packages.html',
                           title=title,
                           packages=records,
                           status_checks=[],
                           commit='commit...tbd')

#@app.route('/legacy/packages', methods=['GET'])
#def _packages():
#    data = _get_data()
#    packages = {}
#
#    developer = request.args.get('developer')
#    status = request.args.get('status')
#    infra = request.args.get('infra')
#
#    if developer is not None:
#        for pkg_name in data['packages']:
#            for dev in data['packages'][pkg_name]['developers']:
#                if dev == developer:
#                    packages[pkg_name] = (data['packages'][pkg_name])
#        title = u'{} package(s) maintained by {}'.format(len(packages), developer)
#
#    elif status is not None:
#        for pkg_name in data['packages']:
#            pkg = data['packages'][pkg_name]
#            if pkg['status'][status][0] != 'ok':
#                packages[pkg_name] = pkg
#        title = u'{} package(s) with {} check status is not ok'.format(len(packages), status)
#
#    elif infra is not None:
#        for pkg_name in data['packages']:
#            pkg = data['packages'][pkg_name]
#            if pkg['infras']:
#                if pkg['infras'][0][1] == infra:
#                    packages[pkg_name] = pkg
#        title = u'{} package(s) with {} infrastructure'.format(len(packages), infra)
#    else:
#        packages = data['packages']
#        title = u'Total amount of packages: {}'.format(len(packages))
#
#    packages = OrderedDict(sorted(packages.items(), key=lambda t: t[0]))
#
#    return render_template('legacy_packages.html',
#                           title=title,
#                           packages=packages,
#                           status_checks=data['package_status_checks'],
#                           commit=data['commit'])


@app.route('/package/<name>')
def package(name):
    record = app.session.query(models.Package).filter_by(name=name).first()
    return render_template('package.html',
                           pkg=record,
                           status_checks=[],
                           commit='commit...tbd')


@app.route('/developers')
def developers():
    records = app.session.query(models.Developer).order_by(models.Developer.name.asc()).all()
    title = u'Total amount of developers: {}'.format(len(records))
    return render_template('developers.html',
                           title=title,
                           developers=records,
                           status_checks=[],
                           commit='commit...tbd')


@app.route('/defconfigs', methods=['GET'])
def defconfigs():
    records = app.session.query(models.Defconfig).order_by(models.Defconfig.name.asc()).all()

    # GET
    developer = request.args.get('developer')

#    if developer is not None:
#        for name in data['defconfigs']:
#            for dev in data['defconfigs'][name]['developers']:
#                if dev == developer:
#                    defconfigs[name] = data['defconfigs'][name]
#
#        title = u'{} defconfig(s) maintained by {}'.format(len(defconfigs), developer)
#    else:
#
#        defconfigs = OrderedDict(sorted(data['defconfigs'].items(), key=lambda t: t[0]))
#        title = u'Total amount of defconfigs: {}'.format(len(defconfigs))
    title = u'Total amount of defconfigs: {}'.format(len(records))

    return render_template('defconfigs.html',
                           title=title,
                           defconfigs=records,
                           status_checks=[],
                           commit='commit...tbd')


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
