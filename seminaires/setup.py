import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='seminaires',
    version='1337',
    packages=find_packages(),
    include_package_data=True,
    license='LJLL hand-made',  # example license
    description='Une application Django/Wagtail qui genere les fichiers .ics (iCalendar) pour permettre une collecte de flux par l\'Agenda des Mathematiques. Les fichiers sont generes depuis les Evenements stockes en base grace au modele de page \'Evenement\'.',
    long_description=README,
    url='https://github.com/cdivry/seminaires',
    author='Clement DIVRY',
    author_email='divry@ljll.math.upmc.fr',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.10.5',
        'Intended Audience :: Developers, Scientists',
        'License :: OSI Approved :: GNU GPL',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
