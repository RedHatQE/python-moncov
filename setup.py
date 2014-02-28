#!/usr/bin/env python

from setuptools import setup
import glob, os

setup(name='moncov',
    version='0.4',
    description='Python code coverage using MongoDB',
    author='Vitaly Kuznetsov',
    author_email='vitty@redhat.com',
    url='https://github.com/RedHatQE/python-moncov',
    license="GPLv3+",
    install_requires=['pymongo', 'cement'],
    packages=[
        'moncov'
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
