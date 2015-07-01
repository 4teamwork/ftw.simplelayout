from ftw.simplelayout.interfaces import IBlockProperties
from plone.i18n.normalizer.interfaces import IIDNormalizer
from zope.component import getUtility
from zope.component import queryMultiAdapter


def normalize_portal_type(portal_type):
    normalizer = getUtility(IIDNormalizer)
    return normalizer.normalize(portal_type)


def get_block_html(block):
    properties = queryMultiAdapter((block, block.REQUEST),
                                   IBlockProperties)
    viewname = properties.get_current_view_name()
    return block.restrictedTraverse(viewname)()
