from ftw.simplelayout import config
from ftw.simplelayout.contents.interfaces import IImageBlock
from plone.app.blob.content import ATBlob
from plone.app.blob.content import ATBlobSchema
from plone.app.blob.content import addATBlob
from Products.Archetypes import atapi
from AccessControl import ClassSecurityInfo
from zope.interface import implements

imagelock_schema = ATBlobSchema.copy()

def addImageBlock(container, id, **kwargs):
    return addATBlob(container, id, subtype='Image', **kwargs)


class ImageBlock(ATBlob):
    """A blockish link type"""
    implements(IImageBlock)

    schema = imagelock_schema
    security = ClassSecurityInfo()


atapi.registerType(ImageBlock, config.PROJECTNAME)

