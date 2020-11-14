from __future__ import print_function

import argparse
import json
import re
import sys

from app import models
from app.database import SessionLocal, engine, Base
from app.gravatar import get_gravatar_url

EMAIL_RE = re.compile(r"^(.*) <(.*)>$")

def import_or_ignore_developer(db, developer):
    match = EMAIL_RE.match(developer)
    if match:
        name = match.group(1)
        email = match.group(2)

    record = db.query(models.Developer).filter_by(email = email).first()
    if record is None:
        url = get_gravatar_url(email)
        record = models.Developer(name=name, email=email, gravatar_url=url)
        db.add(record)
        # we need to commit so further queries will work
        db.commit()

    return record

def import_packages(db, packages_data):
    print("importing packages ...", end='')
    sys.stdout.flush()
    for pkg_name in packages_data:
        pkg = packages_data[pkg_name]

        insert = {}
        insert['name'] = pkg_name
        insert['current_version'] = pkg['current_version']
        insert['latest_version'] = pkg['latest_version']['version']
        insert['latest_version_id'] = pkg['latest_version']['id']
        insert['path'] = pkg['path']
        insert['pkg_path'] = pkg['pkg_path']
        insert['url'] = pkg['url']
        insert['license'] = pkg['license']
        insert['patch_count'] = len(pkg['patch_files'])
        insert['developer_count'] = len(pkg['developers'])
        insert['cve_count'] = len(pkg['cves'])

        p = models.Package(**insert)

        for developer in pkg['developers']:
            record = import_or_ignore_developer(db, developer)
            p.developers.append(record)

        for infra in pkg['infras']:
            i = models.Infrastructure(destination=infra[0], build_system=infra[1])
            db.add(i)
            p.infras.append(i)

        for filename in pkg['patch_files']:
            d = models.Patch(filename=filename)
            db.add(d)
            p.patches.append(d)

        for status in pkg['status']:
            s = models.Status(check=status,
                       result=pkg['status'][status][0],
                       verbose=pkg['status'][status][1])

            db.add(s)
            p.status.append(s)

        for cve in pkg['cves']:
            print(cve)
            c = models.CVE(name=cve)
            db.add(c)
            p.cves.append(c)

        db.add(p)
    db.commit()
    print(' {}'.format(db.query(models.Package).count()))


def import_defconfigs(db, defconfig_data):
    print("importing defconfigs ...", end='')
    sys.stdout.flush()
    for defconfig_name in defconfig_data:
        defconfig = defconfig_data[defconfig_name]
        path = defconfig['path']
        d = models.Defconfig(name=defconfig_name, path=path)

        for developer in defconfig['developers']:
            record = import_or_ignore_developer(db, developer)
            d.developers.append(record)

        db.add(d)

    db.commit()

    print(' {}'.format(db.query(models.Defconfig).count()))


def import_from_json(db, filename):

    data = None
    with open(filename) as json_file:
        data = json.load(json_file)

    import_packages(db, data['packages'])
    import_defconfigs(db, data['defconfigs'])

def cmd_import(args):

    db = SessionLocal()
    print('import')
    # drop all tables
    from sqlalchemy.exc import OperationalError
    for tbl in reversed(Base.metadata.sorted_tables):
        try:
            tbl.drop(engine)
        except OperationalError:
            print("Error deleting {}".format(tbl))
            pass


    # create databases
    Base.metadata.create_all(engine)

    import_from_json(db, args.input)
    pass


def cmd_get_package(args):
    print('get')
    pass


def main(args=None):
    parser = argparse.ArgumentParser(description="buildroot-stats database tool.")

    # commands
    _sub = parser.add_subparsers(title="Commands")

    # import stats
    subparser = _sub.add_parser("import", help="import stats from json")
    subparser.set_defaults(func=cmd_import)
    subparser.add_argument("-i", "--input", required=True, type=str, dest="input", help="input stats file")

    # import get_package
    subparser = _sub.add_parser("package", help="get package")
    subparser.set_defaults(func=cmd_get_package)
    subparser.add_argument("-p", "--package", required=True, type=str, dest="pkg_name", help="pakcakge name")

    args = parser.parse_args(args)

    try:
        args.func(args)
    finally:
        pass


if __name__ == "__main__":
    main()

