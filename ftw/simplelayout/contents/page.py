from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi
from ftw.simplelayout import config
from Products.ATContentTypes.lib.constraintypes import (
    ConstrainTypesMixinSchema)
from Products.ATContentTypes.content.folder import ATFolder
from zope.interface import implements
from Products.CMFCore.utils import getToolByName
from ftw.simplelayout.contents.interfaces import IPage

page_schema = ATFolder.schema.copy() + ConstrainTypesMixinSchema.copy()


class Page(ATFolder):
    implements(IPage)
    security = ClassSecurityInfo()

    schema = page_schema

    def getPageTypes(self):
        catalog = getToolByName(self, "portal_catalog")
        return catalog.uniqueValuesFor("page_types")

atapi.registerType(Page, config.PROJECTNAME)
