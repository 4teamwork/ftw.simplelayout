from collections import OrderedDict
from collective import dexteritytextindexer
from ftw.simplelayout import _
from ftw.simplelayout.browser.actions import DefaultActions
from ftw.simplelayout.contents.interfaces import ITextBlock
from ftw.simplelayout.interfaces import IBlockConfiguration
from ftw.simplelayout.interfaces import IBlockModifier
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


class TextBlockModifier(object):

    implements(IBlockModifier)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def modify(self, data):
        image_scale = data.get('scale', None)
        conf = IBlockConfiguration(self.context)
        blockconf = conf.load()

        if image_scale:
            blockconf['scale'] = image_scale
            conf.store(blockconf)  # necessary?
        return


class TextBlockActions(DefaultActions):

    def specific_actions(self):
        return OrderedDict([('imageLeft', {'class': 'icon-image-left server-action',
                                           'title': 'Float image left',
                                           'href': './sl-ajax-reload-block-view',
                                           'data-scale': 'mini'}),
                            ('image', {'class': 'icon-image server-action',
                                       'title': 'Image without floating',
                                       'href': './sl-ajax-reload-block-view',
                                       'data-scale': 'large'})])
