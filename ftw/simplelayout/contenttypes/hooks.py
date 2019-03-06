from ftw.simplelayout.utils import IS_PLONE_5
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


def profile_uninstalled(site):
    if IS_PLONE_5:
        clean_plone5_registry(site)


def clean_plone5_registry(site):
    registry = getUtility(IRegistry)

    allowed_sizes = registry['plone.allowed_sizes']
    # allowed_sizes.remove(u'colorbox 2000:2000')
    allowed_sizes.remove(u'simplelayout_galleryblock 480:480')
    allowed_sizes.remove(u'sl_textblock_small 480:480')
    allowed_sizes.remove(u'sl_textblock_middle 800:800')
    allowed_sizes.remove(u'sl_textblock_large 1280:1280')
    registry['plone.allowed_sizes'] = allowed_sizes

    types_not_searched = list(registry['plone.types_not_searched'])
    types_not_searched.remove('ftw.simplelayout.TextBlock')
    types_not_searched.remove('ftw.simplelayout.FileListingBlock')
    types_not_searched.remove('ftw.simplelayout.VideoBlock')
    types_not_searched.remove('ftw.simplelayout.GalleryBlock')
    registry['plone.types_not_searched'] = tuple(types_not_searched)

    default_page_types = registry['plone.default_page_types']
    default_page_types.remove(u'ftw.simplelayout.ContentPage')
    registry['plone.default_page_types'] = default_page_types

    contains_objects = registry['plone.contains_objects']
    contains_objects.remove(u'ftw.simplelayout.ContentPage')
    contains_objects.remove(u'ftw.simplelayout.FileListingBlock')
    contains_objects.remove(u'ftw.simplelayout.GalleryBlock')
    registry['plone.contains_objects'] = contains_objects

    displayed_types = list(registry['plone.displayed_types'])
    displayed_types.remove(u'ftw.simplelayout.ContentPage')
    registry['plone.displayed_types'] = tuple(displayed_types)
