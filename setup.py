# -*- coding: utf-8 -*-
"""Setup for quotationtool.workflow package

$Id$
"""
from setuptools import setup, find_packages
import os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

name='quotationtool.workflow'

setup(
    name = name,
    version='0.1.0',
    description="Workflow management for content objects of quotationtool application",
    long_description=(
        read('README')
        + '\n' +
        'Detailed Documentation\n'
        '**********************\n'
        + '\n' +
        read('src', 'quotationtool', 'workflow', 'README.txt')
        + '\n' +
        read('src', 'quotationtool', 'workflow', 'browser', 'README.txt')
        + '\n' +
        'Download\n'
        '********\n'
        ),
    keywords='quotationtool, blue bream',
    author=u"Christian L&uuml;ck",
    author_email='cluecksbox@googlemail.com',
    url='',
    license='ZPL 2.1',
    # Get more from http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=['Programming Language :: Python',
                 'Environment :: Web Environment',
                 'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
                 'Framework :: Zope3',
                 ],
    packages = find_packages('src'),
    namespace_packages = ['quotationtool',],
    package_dir = {'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires = [
        'setuptools',
        'ZODB3',
        'zope.interface',
        'zope.schema',
        'zope.component',
        'zope.security',
        'zope.securitypolicy',
        'zope.annotation',
        'zope.dublincore',
        'zope.exceptions',
        'zope.traversing',
        'zope.app.component',
        'zope.i18n',
        'zope.i18nmessageid',
        'zope.publisher',
        'zope.app.schema',
        'zope.container',
        'zope.wfmc',
        'zope.app.wfmc',
        'z3c.indexer',

        'zope.app.pagetemplate',
        'zope.viewlet',
        'z3c.pagelet',
        'z3c.form',
        'z3c.formui',
        'z3c.template',
        'z3c.macro',
        'z3c.layer.pagelet',
        'zope.browserpage',
        'zope.app.publisher',
        'z3c.menu.ready2go',
        'zc.resourcelibrary',
        'zope.contentprovider',

        'quotationtool.site',
        'quotationtool.security',
        'quotationtool.skin',
        'quotationtool.tinymce',
        'quotationtool.user',

        ],
    extras_require = dict(
        test = [
            'zope.testing',
            'zope.configuration',
            'zope.site',
            'zope.app.testing',
            'quotationtool.relation',

            ],
        ),
    )
