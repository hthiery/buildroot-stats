import time
import json

#from os import (listdir)
#from os.path import (isfile, join)

from flask import (abort, g, render_template, redirect, request, url_for)
#from urllib.parse import quote_plus

from app import app

from . import models

#app.jinja_env.filters['quote_plus'] = lambda u: quote_plus(u)

def _get_data():
    data = None

    try:
        with open('data/latest.json') as json_file:
            data = json.load(json_file)
    except AttributeError:
        abort(404, description="Resource not found")

    return data


#def _get_stats():
#    files = [f for f in listdir('data/stats') if isfile(join('data/stats', f))]
#    files = sorted(files)
#
#    stats = {}
#
#    for f in files:
#        with open('data/stats/'+f) as json_file:
#
#            d = json.load(json_file)
#
#            if 'labels' not in stats:
#                stats['labels'] = []
#            stats['labels'].append(str(d['date'][:10]))
#
#            for k, v in d['stats'].items():
#                if k in 'infras':
#                    continue
#                if k not in stats:
#                    stats[k] = []
#                if k not in d['stats']:
#                    stats[k].append(None)
#                else:
#                    stats[k].append(d['stats'][k])
#
#    return stats


def _get_commit_id():
    commit = app.session.query(models.Common).filter_by(key='commit').first()
    return commit.value


def _get_packages_by_developer(developer):
    return app.session.query(models.Package).filter(models.Package.developers.any(email=developer)).order_by(models.Package.name.asc()).all()


def _get_packages_by_infra(infra):
    return app.session.query(models.Package).filter(models.Package.infras.any(destination='target', build_system=infra)).order_by(models.Package.name.asc()).all()


def _get_packages_by_check_status(check, status):
    print(check, status)
    return app.session.query(models.Package).filter(models.Package.status.any(check=check, result=status)).order_by(models.Package.name.asc()).all()


def _get_all_packages():
    return app.session.query(models.Package).order_by(models.Package.name.asc()).all()


def _get_package_by_name(name):
    return app.session.query(models.Package).filter_by(name=name).first()


def _get_all_developers():
    return app.session.query(models.Developer).order_by(models.Developer.name.asc()).all()


def _get_all_defconfigs():
    return app.session.query(models.Defconfig).order_by(models.Defconfig.name.asc()).all()


def _get_defconfigs_by_developer(developer):
    return app.session.query(models.Defconfig).filter(models.Defconfig.developers.any(email=developer)).order_by(models.Defconfig.name.asc()).all()


def _get_status_checks():
    checks = [
        "license",
        "license-files",
        "hash",
        "hash-license",
        "patches",
        "pkg-check",
        "cpe",
        "url",
        "developers",
        "version",
        "cve"
    ]
    return sorted(checks)


def _get_status_results():
    results = [
        "na",
        "ok",
        "warning",
        "error"
    ]
    return sorted(results)


@app.before_request
def before_request():
    g.request_start_time = time.time()
    g.request_time = lambda: "%.5fs" % (time.time() - g.request_start_time)


@app.errorhandler(404)
def page_not_found(msg):
    return render_template('404.html', msg=msg, commit=''), 404


@app.route('/')
def index():
    return redirect('packages')


@app.route('/packages', methods=['GET'])
def packages():
    commit = _get_commit_id()

    # GET
    developer = request.args.get('developer')
    check = request.args.get('check')
    check_status = request.args.get('status')
    infra = request.args.get('infra')

    if developer is not None:
        pkgs = _get_packages_by_developer(developer)
        title = u'{} package(s) maintained by {}'.format(len(pkgs), developer)
    elif infra is not None:
        pkgs = _get_packages_by_infra(infra)
        title = u'{} package(s) with {} infrastructure'.format(len(pkgs), infra)
    elif check is not None and check_status is not None:
        pkgs = _get_packages_by_check_status(check, check_status)
        title = u'{} package(s) filtered by check {} and status {}'.format(len(pkgs), check, check_status)
    else:
        pkgs = _get_all_packages()
        title = u'Total amount of packages: {}'.format(len(pkgs))

    return render_template('packages.html',
                           title=title,
                           status_checks=_get_status_checks(),
                           status_results=_get_status_results(),
                           commit=commit,
                           packages=pkgs)


@app.route('/status/<name>')
def status(name):
    package = _get_package_by_name(name)
    status = {}
    for s in package.status:
        status[s.check] = {'result': s.result, 'verbose': s.verbose}
    return json.dumps(status)


@app.route('/package/<name>')
def package(name):
    commit = _get_commit_id()
    pkg = _get_package_by_name(name)
    return render_template('package.html',
                           status_checks=_get_status_checks(),
                           status_results=_get_status_results(),
                           commit=commit,
                           pkg=pkg)


@app.route('/developers')
def developers():
    commit = _get_commit_id()
    devs = _get_all_developers()
    title = u'Total amount of developers: {}'.format(len(devs))
    return render_template('developers.html',
                           title=title,
                           status_checks=_get_status_checks(),
                           status_results=_get_status_results(),
                           commit=commit,
                           developers=devs)


@app.route('/defconfigs', methods=['GET'])
def defconfigs():
    commit = _get_commit_id()

    # GET
    developer = request.args.get('developer')

    if developer is not None:
        defs = _get_defconfigs_by_developer(developer)
        title = u'{} defconfig(s) maintained by {}'.format(len(defs), developer)
    else:
        defs = _get_all_defconfigs()
        title = u'Total amount of defconfigs: {}'.format(len(defs))

    return render_template('defconfigs.html',
                           title=title,
                           status_checks=_get_status_checks(),
                           status_results=_get_status_results(),
                           commit=commit,
                           defconfigs=defs)


#@app.route('/stats')
#def stats():
#    data = None
#    stats = None
#
#    data = _get_data()
#    stats = _get_stats()
#
#    return render_template('stats.html',
#                           stats=stats,
#                           status_checks=_get_status_checks(),
#                           status_results= _get_status_results(),
#                           commit=commit)


@app.route('/json')
def json_stats():
    # add a symlink to data/latest.json into static/lastest.json
    return redirect(url_for('static', filename='latest.json'))
