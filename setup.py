#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2010-2013 Código Sur Sociedad Civil
# All rights reserved.
#
# This file is part of Cyclope.
#
# Cyclope is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Cyclope is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import codecs
from setuptools import setup, find_packages

version = '0.4.1.2'


def read(filename):
    return unicode(codecs.open(filename, encoding='utf-8').read())


long_description = '\n\n'.join([read('README.rst'),
                                read('CONTRIBUTORS.rst'),
                                read('CHANGELOG.rst')])

setup(
    name='cyclope3',
    version=version,
    description="CMS for pythonistas who like to code instead of using a web UI for every task.",
    long_description=long_description,
    author='Nicolás Echániz & Santiago Hoerth',
    author_email='nicoechaniz@codigosur.org',
    maintainer='Santiago Piccinini',
    maintainer_email='spiccinini@codigosur.org',
    url='http://forja.codigosur.org/projects/cyclope/',
    license='GPL v3',
    platforms=['OS Independent'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],

    install_requires=[
        'Django>=1.4,<1.5',
        'django-autoslug==1.4.1',
        'django-mptt==0.4.2', # 0.4 breaks compatibility
        'django-mptt-tree-editor>=0.1.1,<0.2',
        'Pillow>=2.0',# python >= 2.6
        'django-simple-captcha==0.4.1',
        'django-filebrowser-nograpup>=3.0.3,<3.1',
        'South>=0.7,<0.8',
        'django-registration==0.8',
        'django-profiles==0.2',
        'django-admin-tools==0.4.1',
        'Whoosh>=2.4.1,<2.5',
        'django-haystack>=1.2.7,<1.3',
        'textile==2.1.4',
        'django-dbgettext>=0.1',
        'django-rosetta==0.7.2',
        'django-markitup==2.3.1',
        'django-jsonfield==0.9.10',
        'feedparser==5.1',
        'django-forms-builder>=0.7.5,<0.8',
        'django-threadedcomments==0.9.0',
        'django-crispy-forms==1.5.2',
        'django-compressor>=1.2,<1.3',
        'django-generic-ratings>=0.6,<0.7',
        'django-activity-stream==0.4.4',
        'python-memcached',
    ],

    scripts=['cyclope/bin/cyclopeproject'],

    packages=find_packages(),

    include_package_data=True,
    zip_safe=False,
)
