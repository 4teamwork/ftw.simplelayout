from plone.registry.interfaces import IRegistry
from zope.component import getUtility
import pkg_resources


IS_PLONE_5 = pkg_resources.get_distribution('Products.CMFPlone').version >= '5'


def installed(site):
    if IS_PLONE_5:
        add_plone_5_registry(site)


def uninstalled(site):
    if IS_PLONE_5:
        remove_plone_5_registry(site)


def add_plone_5_registry(site):
    registry = getUtility(IRegistry)
    types_not_searched = list(registry['plone.types_not_searched'])
    types_not_searched.append('ftw.simplelayout.AliasBlock')
    registry['plone.types_not_searched'] = tuple(types_not_searched)


def remove_plone_5_registry(site):
    registry = getUtility(IRegistry)
    types_not_searched = list(registry['plone.types_not_searched'])
    types_not_searched.remove('ftw.simplelayout.AliasBlock')
    registry['plone.types_not_searched'] = tuple(types_not_searched)
