from ftw.simplelayout import config
from ftw.simplelayout.contents.interfaces import IFileBlock
from plone.app.blob.content import ATBlob
from plone.app.blob.content import ATBlobSchema
from plone.app.blob.content import addATBlob
from Products.Archetypes import atapi
from AccessControl import ClassSecurityInfo
from zope.interface import implements


fileblock_schema = ATBlobSchema.copy()


def addFileBlock(container, id_, **kwargs):
    return addATBlob(container, id_, subtype='File', **kwargs)


class FileBlock(ATBlob):
    """A blockish link type"""
    implements(IFileBlock)

    schema = fileblock_schema
    security = ClassSecurityInfo()


atapi.registerType(FileBlock, config.PROJECTNAME)
