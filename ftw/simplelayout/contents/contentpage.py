from plone.dexterity.content import Container
from plone.supermodel import model
from zope.interface import implements
from ftw.simplelayout.contents.interfaces import IContentPage


class IContentPageSchema(model.Schema):
    """A Folderish page type for blocks
    """


class ContentPage(Container):
    implements(IContentPage)
