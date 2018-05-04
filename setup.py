import os
import sys
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

postgresql_extras = ['psycopg2>=2.4.2']
dev_extras = []

extras_require = dict(
    dev=dev_extras,
    postgresql=postgresql_extras,
)

requires = [
    'ott.utils',
    'gtfsdb',
    'ott.gtfsdb_realtime',
    'transaction',
    'simplejson',
    'usaddress', # crfsuite pre-built binaries -- https://github.com/estnltk/estnltk/tree/master/dist/python-crfsuite
    # note: download 'raw' file from github, then use PowerShell to install
]


setup(
    name='ott.data',
    version='0.1.0',
    description='Open Transit Tools - OTT Database',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author="Open Transit Tools",
    author_email="info@opentransittools.org",
    dependency_links=[
        'git+https://github.com/OpenTransitTools/utils.git#egg=ott.utils-0.1.0',
        'git+https://github.com/OpenTransitTools/gtfsdb.git#egg=gtfsdb-1.0.0',
        'git+https://github.com/OpenTransitTools/gtfsdb_realtime.git#egg=ott.gtfsdb_realtime-1.0.0',
    ],
    license="Mozilla-derived (http://opentransittools.com)",
    url='http://opentransittools.com',
    keywords='ott, otp, gtfs, gtfsdb, data, database, services, transit',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    extras_require=extras_require,
    tests_require=requires,
    test_suite="ott.data.tests",
    entry_points="""\
        [console_scripts]
        load_rt = ott.data.gtfsrdb.gtfsrdb:main
        test_main = ott.data.tests.main:main
    """,
)
