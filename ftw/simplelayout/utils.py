from ftw.simplelayout.interfaces import IBlockProperties
from ftw.simplelayout.interfaces import ISimplelayoutBlock
from plone.dexterity.interfaces import IDexterityFTI
from plone.i18n.normalizer.interfaces import IIDNormalizer
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.component import queryUtility
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
    typeids = types_tool.objectIds()
    typeids.sort()
    for type_id in typeids:
        dx_fti = queryUtility(IDexterityFTI, name=type_id)
        if not dx_fti:
            continue
        else:
            if ISimplelayoutBlock.__identifier__ in dx_fti.behaviors:
                yield dx_fti
