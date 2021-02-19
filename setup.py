from setuptools import setup, find_packages
import os

version = '2.0.3'
maintainer = 'Mathias Leimgruber'

tests_require = [
    'Products.CMFPlone',
    'Products.GenericSetup',
    'ftw.builder',
    'ftw.testbrowser',
    'ftw.testing',
    'ftw.trash',
    'path.py',
    'plone.app.lockingbehavior',
    'plone.app.testing',
    'plone.testing',
    'transaction',
    'unittest2',
    'zope.configuration',
    'ftw.simplelayout [trash, mapblock]',
]

extras_require = {
    'tests': tests_require,
    'test': tests_require,
    'contenttypes': [
        'ftw.colorbox >= 1.3.0',
        'ftw.table >= 1.22.0',
        'ftw.upgrade',
        'plone.app.dexterity',
        'plone.app.relationfield',
        'plone.autoform',
        'plone.behavior',
        'plone.dexterity',
        'plone.directives.form',
        'ftw.iframefix',
        'ftw.referencewidget >= 2.1.0',
    ],
    'mapblock': [
        'collective.geo.bundle [dexterity]',
    ],
    'plone4': [
        'plone.app.referenceablebehavior',
        'collective.quickupload',
    ],
    'trash': [
        'ftw.trash',
    ]
}


setup(name='ftw.simplelayout',
      version=version,
      description='SimpleLayout provides block based content pages',
      long_description=open('README.rst').read() + '\n' +
          open(os.path.join('docs', 'HISTORY.txt')).read(),

      # Get more strings from
      # http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          'Framework :: Plone',
          'Framework :: Plone :: 4.3',
          'Framework :: Plone :: 5.1',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Topic :: Software Development :: Libraries :: Python Modules',
          ],

      keywords='ftw plone simplelayout block contentpage',
      author='4teamwork AG',
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
          'collective.dexteritytextindexer',
          'collective.js.jqueryui',
          # 'cssutils', # TODO: is this used anywhere?
          'Persistence',
          'ftw.autofeature',
          'plone.api',
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
          'z3c.form>=3.2.9',
          'Plone',
          'ftw.theming>=1.7.0',
          ],

      tests_require=tests_require,
      extras_require=extras_require,

      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
