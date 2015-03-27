#!/usr/bin/env python

from setuptools import setup
import glob, os

setup(name='moncov',
    version='0.5.16',
    description='Python remote code coverage using Redis',
    author='Vitaly Kuznetsov',
    author_email='vitty@redhat.com',
    url='https://github.com/RedHatQE/python-moncov',
    license="GPLv3+",
    provides=['moncov'],
    install_requires=['redis', 'hiredis', 'aaargh', 'PyYAML', 'lxml', 'coverage'],
    packages=[
        'moncov',
        'moncov/stats'
        ],
    scripts=['bin/moncov'],
    data_files=[
        ('/etc', ['etc/moncov.yaml']),
        ('/usr/lib/systemd/system', ['lib/systemd/system/moncov.service'])
    ],
    classifiers=[
            'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
            'Programming Language :: Python',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Operating System :: POSIX',
            'Intended Audience :: Developers',
            'Development Status :: 4 - Beta'
    ]
)
