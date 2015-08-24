from ftw.simplelayout.contenttypes.contents.interfaces import IContentPage
from plone.dexterity.content import Container
from plone.supermodel import model
from zope.interface import implements


class IContentPageSchema(model.Schema):
    """A Folderish page type for blocks
    """


class ContentPage(Container):
    implements(IContentPage)
