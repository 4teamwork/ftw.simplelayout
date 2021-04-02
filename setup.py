from setuptools import setup, find_packages
import os

version = '2.8.0'
maintainer = 'Mathias Leimgruber'

tests_require = [
    'Products.CMFPlone',
    'Products.GenericSetup',
    'ftw.builder',
    'ftw.file',
    'ftw.testbrowser',
    'ftw.testing',
    'ftw.trash',
    'path.py',
    'plone.app.contenttypes',
    'plone.app.lockingbehavior',
    'plone.app.testing',
    'plone.restapi',
    'plone.testing',
    'transaction',
    'zope.configuration',
    'ftw.simplelayout [trash, mapblock]',
    'ftw.logo',
]

extras_require = {
    'tests': tests_require,
    'test': tests_require,
    'contenttypes': [
        # Deprecated
    ],
    'mapblock': [
        'collective.geo.bundle [dexterity]',
    ],
    'plone4': [
        'plone.app.referenceablebehavior',
        'ftw.uploadutility',
        'collective.quickupload',
    ],
    'trash': [
        'ftw.trash',
    ],
    'restapi': [
        'plone.restapi',
    ],
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
          'AccessControl',
          'Acquisition',
          'Persistence',
          'Plone',
          'Products.ATContentTypes',
          'Products.Archetypes',
          'Products.CMFCore',
          'Zope2',
          'collective.dexteritytextindexer',
          'collective.js.jqueryui',
          'ftw.autofeature',
          'ftw.colorbox >= 1.6.0',
          'ftw.iframefix',
          'ftw.referencewidget >= 2.1.0',
          'ftw.table >= 1.22.0',
          'ftw.theming>=1.7.0',
          'ftw.upgrade',
          'plone.api',
          'plone.app.blob',
          'plone.app.dexterity',
          'plone.app.relationfield',
          'plone.autoform',
          'plone.behavior',
          'plone.dexterity',
          'plone.directives.form',
          'plone.uuid',
          'setuptools',
          'z3c.form>=3.2.9',
          'zExceptions',
          'zope.annotation',
          'zope.component',
          'zope.event',
          'zope.i18nmessageid',
          'zope.interface',
          'zope.lifecycleevent',
          'zope.publisher',
          ],

      tests_require=tests_require,
      extras_require=extras_require,

      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
