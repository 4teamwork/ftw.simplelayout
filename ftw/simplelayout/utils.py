from ftw.simplelayout.interfaces import IBlockProperties
from ftw.simplelayout.interfaces import ISimplelayoutBlock
from plone.dexterity.interfaces import IDexterityFTI
from plone.i18n.normalizer.interfaces import IIDNormalizer
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.component.hooks import getSite


def normalize_portal_type(portal_type):
    normalizer = getUtility(IIDNormalizer)
    return normalizer.normalize(portal_type)


def get_block_html(block):
    properties = queryMultiAdapter((block, block.REQUEST),
                                   IBlockProperties)
    viewname = properties.get_current_view_name()
    return block.restrictedTraverse(viewname)()


def get_block_types():
    platform = getSite()
    types_tool = getToolByName(platform, 'portal_types')

    dexterity_ftis = filter(
        IDexterityFTI.providedBy, types_tool.objectValues())

    return filter(
        lambda fti: ISimplelayoutBlock.__identifier__ in fti.behaviors,
        dexterity_ftis)
