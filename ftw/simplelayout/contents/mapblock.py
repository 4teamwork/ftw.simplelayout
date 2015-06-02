from ftw.simplelayout import _
from ftw.simplelayout.contents.interfaces import IMapBlock
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Item
from plone.directives import form
from zope import schema
from zope.interface import alsoProvides
from zope.interface import implements


class IMapBlockSchema(form.Schema):
    """MapBlock for simplelayout
    """

    # title = schema.TextLine(
    #     title=_(u'label_title', default=u'Title'),
    #     required=False)

alsoProvides(IMapBlockSchema, IFormFieldProvider)


class MapBlock(Item):
    implements(IMapBlock)
