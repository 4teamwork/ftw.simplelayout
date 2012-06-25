from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi
from ftw.simplelayout import config
from Products.ATContentTypes.lib.constraintypes import (
    ConstrainTypesMixinSchema)
from Products.ATContentTypes.content.folder import ATFolder
from zope.interface import implements
from ftw.simplelayout.contents.interfaces import IPage

page_schema = ATFolder.schema.copy() + ConstrainTypesMixinSchema.copy()


class Page(ATFolder):
    implements(IPage)
    security = ClassSecurityInfo()

    schema = page_schema


atapi.registerType(Page, config.PROJECTNAME)
