from AccessControl import ClassSecurityInfo
from ftw.simplelayout import config
from ftw.simplelayout.contents.interfaces import IFileBlock
from plone.app.blob.content import ATBlob
from plone.app.blob.content import ATBlobSchema
from plone.app.blob.content import hasCMF22
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
    if subtype is not None:
        markAs(obj, subtype)    # mark with interfaces needed for subtype
    if not hasCMF22:
        notify(ObjectCreatedEvent(obj))
    container._setObject(id_, obj, suppress_events=hasCMF22)
    obj = container._getOb(id_)
    if hasCMF22:
        obj.manage_afterAdd(obj, container)
    obj.initializeArchetype(**kwargs)
    if not hasCMF22:
        notify(ObjectModifiedEvent(obj))
    return obj.getId()



class FileBlock(ATBlob):
    """A blockish link type"""
    implements(IFileBlock)

    schema = fileblock_schema
    security = ClassSecurityInfo()


atapi.registerType(FileBlock, config.PROJECTNAME)
