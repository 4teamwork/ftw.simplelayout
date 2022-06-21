from ftw.simplelayout.contenttypes.contents.interfaces import IMediaFolder
from plone.dexterity.content import Container
from plone.supermodel import model
from zope.interface import implements


class IMediaFolderSchema(model.Schema):
    """A Folderish for media types (like files and images)
    """


class MediaFolder(Container):
    implements(IMediaFolder)
