from setuptools import setup, find_packages
import os

version = '1.0a1'
maintainer = 'Mathias Leimgruber'

tests_require = [
    'ftw.builder',
    'ftw.testing',
    'plone.app.testing',
    'plone.testing',
    'Products.CMFPlone',
    'Products.GenericSetup',
    'transaction',
    'unittest2',
    'zope.configuration',
    ]

extras_require = {
    'tests': tests_require,
    'test': tests_require,
    }

setup(name='ftw.simplelayout',
      version=version,
      description='SimpleLayout provides block based content pages',
      long_description=open('README.rst').read() + '\n' + \
          open(os.path.join('docs', 'HISTORY.txt')).read(),

      # Get more strings from
      # http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Plone',
        'Framework :: Plone :: 4.2',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],

      keywords='ftw plone simplelayout block contentpage',
      author='4teamwork GmbH',
      author_email='mailto:info@4teamwork.ch',
      maintainer=maintainer,
      url='https://github.com/4teamwork/ftw.simplelayout',
      license='GPL2',

      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ftw', ],
      include_package_data=True,
      zip_safe=False,

      install_requires=[
        'setuptools',

        'AccessControl',
        'Acquisition',
        'collective.js.jqueryui',
        'Persistence',
        'plone.app.blob',
        'plone.uuid',
        'Products.Archetypes',
        'Products.ATContentTypes',
        'Products.CMFCore',
        'zExceptions',
        'zope.annotation',
        'zope.component',
        'zope.event',
        'zope.i18nmessageid',
        'zope.interface',
        'zope.lifecycleevent',
        'zope.publisher',
        'Zope2',

        ],

      tests_require=tests_require,
      extras_require=extras_require,

      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
