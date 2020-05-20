from ftw.simplelayout import _
from ftw.simplelayout.aliasblock.contents.interfaces import IAliasBlock
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Item
from plone.directives import form
from zope import schema
from zope.interface import alsoProvides
from zope.interface import implements


class IAliasBlockSchema(form.Schema):
    """AliasBlock for simplelayout
    """

    title = schema.TextLine(
        title=_(u'label_title', default=u'Title'),
        required=False)


alsoProvides(IAliasBlockSchema, IFormFieldProvider)


class AliasBlock(Item):
    implements(IAliasBlock)
