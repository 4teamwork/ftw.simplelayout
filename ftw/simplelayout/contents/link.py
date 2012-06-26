from ftw.simplelayout import config
from ftw.simplelayout.contents.interfaces import ILinkBlock
from Products.ATContentTypes.content.link import ATLink
from Products.ATContentTypes.content.link import ATLinkSchema
from Products.Archetypes import atapi
from AccessControl import ClassSecurityInfo
from zope.interface import implements

linkblock_schema = ATLinkSchema.copy()


class LinkBlock(ATLink):
    """A blockish link type"""
    implements(ILinkBlock)

    schema = linkblock_schema
    security = ClassSecurityInfo()


atapi.registerType(LinkBlock, config.PROJECTNAME)
