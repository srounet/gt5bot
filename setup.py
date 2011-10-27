#!/usr/bin/env python

from setuptools import setup

version='1.0'

setup(
    name = 'gt5bot',
    version = version,
    description = 'Gran turismo 5 bspec bot',
    author = 'Fabien Reboia',
    author_email = 'srounet@gmail.com',
    maintainer = 'Fabien Reboia',
    license = 'beer-ware',
    url = 'http://github.com/srounet/gt5bot',
    entry_points = """\
    [console_scripts]
    bspec_bot=gt5bot.scripts:bspec_bot
    """,
    classifiers = [
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Other Audience",
        "License :: Beerware",
        "Natural Language :: English",
        "Operating System :: Unix",
        "Programming Language :: Python :: 2",
        "Topic :: Games/Entertainment :: Automation",
    ]
)
