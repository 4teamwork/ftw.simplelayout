from AccessControl import ClassSecurityInfo
from ftw.simplelayout import config
from ftw.simplelayout.contents.interfaces import IImageBlock
from plone.app.blob.content import ATBlob
from plone.app.blob.content import ATBlobSchema
from plone.app.blob.content import hasCMF22
from plone.app.blob.markings import markAs
from Products.Archetypes import atapi
from zope.event import notify
from zope.interface import implements
from zope.lifecycleevent import ObjectCreatedEvent
from zope.lifecycleevent import ObjectModifiedEvent


imagelock_schema = ATBlobSchema.copy()


def addImageBlock(container, id_, **kwargs):
    subtype = 'Image'
    obj = ImageBlock(id_)
    markAs(obj, subtype)    # mark with interfaces needed for subtype
    notify(ObjectCreatedEvent(obj))
    # pylint: disable=W0212
    container._setObject(id_, obj, suppress_events=hasCMF22)
    obj = container._getOb(id_)
    # pylint: enable=W0212
    obj.initializeArchetype(**kwargs)
    notify(ObjectModifiedEvent(obj))
    return obj.getId()


class ImageBlock(ATBlob):
    """A blockish link type"""
    implements(IImageBlock)

    schema = imagelock_schema
    security = ClassSecurityInfo()


atapi.registerType(ImageBlock, config.PROJECTNAME)
