from ftw.simplelayout.utils import IS_PLONE_5
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


def profile_uninstalled(site):
    if IS_PLONE_5:
        clean_plone5_registry(site)


def clean_plone5_registry(site):
    registry = getUtility(IRegistry)

    types_not_searched = list(registry['plone.types_not_searched'])
    if 'ftw.simplelayout.MapBlock' in types_not_searched:
        types_not_searched.remove('ftw.simplelayout.MapBlock')
        registry['plone.types_not_searched'] = tuple(types_not_searched)
