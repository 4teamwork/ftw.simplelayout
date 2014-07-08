from collective import dexteritytextindexer
from ftw.simplelayout import _
from ftw.simplelayout.contents.interfaces import ITextBlock
from plone.app.textfield import RichText
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Item
from plone.directives import form
from plone.namedfile.field import NamedBlobImage
from zope import schema
from zope.interface import alsoProvides
from zope.interface import implements


class ITextBlockSchema(form.Schema):
    """TextBlock for simplelayout
    """

    title = schema.TextLine(
        title=_(u'label_title', default=u'Title'),
        required=False)

    show_title = schema.Bool(
        title=_(u'label_show_title', default=u'Show title'),
        default=True,
        required=False)

    dexteritytextindexer.searchable('text')
    text = RichText(
        title=_(u'label_text', default=u'Text'),
        required=False)

    form.primary('image')
    image = NamedBlobImage(
        title=_(u'label_image', default=u'Image'),
        required=False)

alsoProvides(ITextBlockSchema, IFormFieldProvider)


class TextBlock(Item):
    implements(ITextBlock)
