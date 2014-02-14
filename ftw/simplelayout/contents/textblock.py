from ftw.simplelayout import _
from ftw.simplelayout.contents.interfaces import ITextBlock
from plone.app.textfield import RichText
from plone.dexterity.content import Item
from plone.namedfile.field import NamedBlobImage
from plone.supermodel import model
from zope import schema
from zope.interface import implements


class ITextBlockSchema(model.Schema):
    """TextBlock for simplelayout
    """

    title = schema.TextLine(title=_(u'label_title', default=u'Title'))

    show_title = schema.Bool(
        title=_(u'label_show_title', default=u'Show title'),
        default=True)

    text = RichText(title=_(u'label_text', default=u'Text'))

    image = NamedBlobImage(title=_(u'label_image', default=u'Image'),
                           required=False)


class TextBlock(Item):
    implements(ITextBlock)
