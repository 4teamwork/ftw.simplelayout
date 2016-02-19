from collections import OrderedDict
from collective import dexteritytextindexer
from ftw.simplelayout import _
from ftw.simplelayout.browser.actions import DefaultActions
from ftw.simplelayout.contenttypes.contents.interfaces import ITextBlock
from ftw.simplelayout.interfaces import IBlockConfiguration
from ftw.simplelayout.interfaces import IBlockModifier
from plone.app.textfield import RichText
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Item
from plone.directives import form
from plone.namedfile.field import NamedBlobImage
from zope import schema
from zope.i18n import translate
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
        required=False,
        allowed_mime_types=('text/html',))

    form.primary('image')
    image = NamedBlobImage(
        title=_(u'label_image', default=u'Image'),
        required=False)

    image_alt_text = schema.TextLine(
        title=_(u'label_image_alt_text', default=u'Image alternative text'),
        required=False)

    open_image_in_overlay = schema.Bool(
        title=_(u'label_open_image_in_overlay',
                default=u'Open image in overlay'
                u' (only if there is no teaser url)'),
        default=False,
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
        image_float = data.get('imagefloat', None)
        image_shadow = data.get('imageshadow', None)
        conf = IBlockConfiguration(self.context)
        blockconf = conf.load()

        if image_shadow and blockconf.get('imageshadow', None) is not None:
            blockconf['imageshadow'] = not blockconf['imageshadow']
        else:
            blockconf['imageshadow'] = True

        if image_scale:
            blockconf['scale'] = image_scale
            blockconf['imagefloat'] = image_float
        conf.store(blockconf)  # necessary?
        return


class TextBlockActions(DefaultActions):

    def specific_actions(self):
        return OrderedDict([
            ('imageLeft', {
                'class': 'icon-image-left server-action',
                'title': translate(
                    _(u'label_float_image_left', default=u'Float image left'),
                    context=self.request),
                'href': './sl-ajax-reload-block-view',
                'data-scale': 'sl_textblock_small',
                'data-imagefloat': 'left'
            }),
            ('imageLeftLarge', {
                'class': 'icon-image-left-large server-action',
                'title': translate(
                    _(u'label_float_large_image_left',
                      default=u'Float large image left'),
                    context=self.request),
                'href': './sl-ajax-reload-block-view',
                'data-scale': 'sl_textblock_middle',
                'data-imagefloat': 'left'
            }),
            ('image', {
                'class': 'icon-image server-action',
                'title': translate(
                    _(u'label_image_without_floating',
                      default=u'Image without floating'),
                    context=self.request),
                'href': './sl-ajax-reload-block-view',
                'data-scale': 'sl_textblock_large',
                'data-imagefloat': 'no-float'
            }),
            ('imageRightLarge', {
                'class': 'icon-image-right-large server-action',
                'title': translate(
                    _(u'label_float_large_image_right',
                      default=u'Float large image right'),
                    context=self.request),
                'href': './sl-ajax-reload-block-view',
                'data-scale': 'sl_textblock_middle',
                'data-imagefloat': 'right'
            }),
            ('imageRight', {
                'class': 'icon-image-right server-action',
                'title': translate(
                    _(u'label_float_image_right',
                      default=u'Float image right'),
                    context=self.request),
                'href': './sl-ajax-reload-block-view',
                'data-scale': 'sl_textblock_small',
                'data-imagefloat': 'right'
            }),
            ('imageShadow', {
                'class': 'icon-image-shadow server-action',
                'title': translate(
                    _(u'label_image_shadow',
                      default=u'Apply shadow to image'),
                    context=self.request),
                'href': './sl-ajax-reload-block-view',
                'data-imageshadow': 'toggle'
            }),
        ])
