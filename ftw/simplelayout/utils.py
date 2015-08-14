from ftw.simplelayout.interfaces import IATSimplelayoutBlockFTIs
from ftw.simplelayout.interfaces import IBlockProperties
from ftw.simplelayout.interfaces import ISimplelayoutBlock
from plone.dexterity.interfaces import IDexterityFTI
from plone.i18n.normalizer.interfaces import IIDNormalizer
from Products.CMFCore.utils import getToolByName
from zope.component import getUtilitiesFor
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

    at_ftis = []
    for name, util in getUtilitiesFor(IATSimplelayoutBlockFTIs):
        at_ftis.extend(util.ftis())

    ftis = []
    for fti in types_tool.objectValues():
        if (IDexterityFTI.providedBy(fti)
                and ISimplelayoutBlock.__identifier__ in fti.behaviors):
            ftis.append(fti)

        elif fti.id in at_ftis:
            ftis.append(fti)

    return ftis
