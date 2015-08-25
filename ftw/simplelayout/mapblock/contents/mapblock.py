from ftw.simplelayout.mapblock.contents.interfaces import IMapBlock
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Item
from plone.directives import form
from zope.interface import alsoProvides
from zope.interface import implements


class IMapBlockSchema(form.Schema):
    """MapBlock for simplelayout
    """

alsoProvides(IMapBlockSchema, IFormFieldProvider)


class MapBlock(Item):
    implements(IMapBlock)
