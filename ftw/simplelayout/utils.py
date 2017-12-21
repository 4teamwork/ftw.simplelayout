from ftw.simplelayout.interfaces import IBlockProperties
from ftw.simplelayout.interfaces import ISimplelayoutBlock
from pkg_resources import get_distribution
from plone import api
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import safe_utf8
from plone.i18n.normalizer.interfaces import IIDNormalizer
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.component.hooks import getSite
import pkg_resources


try:
    pkg_resources.get_distribution('ftw.trash')
except pkg_resources.DistributionNotFound:
    FTW_TRASH_SUPPORT = False
else:
    FTW_TRASH_SUPPORT = True
    from ftw.trash.interfaces import ITrashed


IS_PLONE_5 = get_distribution('Plone').version >= '5'


def normalize_portal_type(portal_type):
    normalizer = getUtility(IIDNormalizer)
    return normalizer.normalize(portal_type)


def get_block_html(block):
    properties = queryMultiAdapter((block, block.REQUEST),
                                   IBlockProperties)
    viewname = properties.get_current_view_name()
    return block.restrictedTraverse(safe_utf8(viewname))()


def get_block_types():
    platform = getSite()
    types_tool = getToolByName(platform, 'portal_types')

    dexterity_ftis = filter(
        IDexterityFTI.providedBy, types_tool.objectValues())

    return filter(
        lambda fti: ISimplelayoutBlock.__identifier__ in fti.behaviors,
        dexterity_ftis)


def unrestricted_uuidToObject(uuid):
    platform = getSite()
    catalog = getToolByName(platform, 'portal_catalog', None)
    if catalog is None:
        return None

    result = catalog.unrestrictedSearchResults(UID=uuid)
    if len(result) != 1:
        return None

    with api.env.adopt_roles(roles=['Manager']):
        return result[0].getObject()


def is_trashed(obj):
    if FTW_TRASH_SUPPORT:
        return ITrashed.providedBy(obj)
    return False
