from AccessControl import ClassSecurityInfo
from ftw.simplelayout import config
from ftw.simplelayout.contents.interfaces import IFileBlock
from plone.app.blob.content import ATBlob
from plone.app.blob.content import ATBlobSchema
from plone.app.blob.markings import markAs
from Products.Archetypes import atapi
from zope.event import notify
from zope.interface import implements
from zope.lifecycleevent import ObjectCreatedEvent
from zope.lifecycleevent import ObjectModifiedEvent


fileblock_schema = ATBlobSchema.copy()



def addFileBlock(container, id_, **kwargs):
    subtype = 'File'
    obj = FileBlock(id_)
    markAs(obj, subtype)    # mark with interfaces needed for subtype

    notify(ObjectCreatedEvent(obj))
    # pylint: disable=W0212
    container._setObject(id_, obj, suppress_events=False)
    obj = container._getOb(id_)
    # pylint: enable=W0212
    obj.initializeArchetype(**kwargs)
    notify(ObjectModifiedEvent(obj))
    return obj.getId()


class FileBlock(ATBlob):
    """A blockish link type"""
    implements(IFileBlock)

    schema = fileblock_schema
    security = ClassSecurityInfo()


atapi.registerType(FileBlock, config.PROJECTNAME)
