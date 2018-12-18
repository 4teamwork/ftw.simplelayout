from collections import OrderedDict
from collective import dexteritytextindexer
from ftw.simplelayout import _
from ftw.simplelayout.browser.actions import DefaultActions
from ftw.simplelayout.contenttypes.contents.interfaces import ITextBlock
from ftw.simplelayout.images.limits.validators import ImageLimitValidator
from ftw.simplelayout.interfaces import IBlockConfiguration
from ftw.simplelayout.interfaces import IBlockModifier
from plone.app.textfield import RichText
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Item
from plone.directives import form
from plone.namedfile.field import NamedBlobImage
from z3c.form import validator
from zope import schema
from zope.i18n import translate
from zope.interface import alsoProvides
from zope.interface import implements


class ITextBlockSchema(form.Schema):

    """TextBlock for simplelayout
    """

    form.fieldset('image',
                  label=_(u'Image'),
                  fields=['image', 'image_alt_text', 'image_caption',
                          'open_image_in_overlay']
                  )

    title = schema.TextLine(
        title=_(u'label_title', default=u'Title'),
        required=False)

    show_title = schema.Bool(
        title=_(u'label_show_title', default=u'Show title'),
        default=True,
        required=False)

    dexteritytextindexer.searchable('text')
    form.primary('text')
    text = RichText(
        title=_(u'label_text', default=u'Text'),
        required=False,
        allowed_mime_types=('text/html',))

    image = NamedBlobImage(
        title=_(u'label_image', default=u'Image'),
        required=False)

    image_alt_text = schema.TextLine(
        title=_(u'label_image_alt_text', default=u'Image alternative text'),
        required=False,
        description=_(u'description_image_alt_text',
                      default=u'Enter an alternative text for the image'))

    image_caption = schema.TextLine(
        title=_(u'label_image_caption', default=u'Image caption'),
        required=False)

    open_image_in_overlay = schema.Bool(
        title=_(u'label_open_image_in_overlay',
                default=u'Open image in overlay'
                u' (only if there is no teaser url)'),
        default=False,
        required=False,
        description=_(u'description_image_clickable',
                      default=u'Opens image in an overlay'))


alsoProvides(ITextBlockSchema, IFormFieldProvider)


class TextBlockImageLimitValidator(ImageLimitValidator):

    identifier = 'ftw.simplelayout.TextBlock'


validator.WidgetValidatorDiscriminators(
    TextBlockImageLimitValidator,
    field=ITextBlockSchema['image']
)


class TextBlock(Item):
    implements(ITextBlock)

    @property
    def additional_css_classes(self):
        if self.title and not (self.image or self.text):
            return ['titleOnly']
        else:
            return []


class TextBlockModifier(object):

    implements(IBlockModifier)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def modify(self, data):
        image_scale = data.get('scale', None)
        image_float = data.get('imagefloat', None)
        conf = IBlockConfiguration(self.context)
        blockconf = conf.load()

        if image_scale:
            blockconf['scale'] = image_scale
            blockconf['imagefloat'] = image_float
            conf.store(blockconf)  # necessary?
        return


class TextBlockActions(DefaultActions):

    def specific_actions(self):
        return OrderedDict([
            ('imageLeft', {
                'class': 'sl-icon-image-left block-server-action',
                'title': translate(
                    _(u'label_float_image_left', default=u'Float image left'),
                    context=self.request),
                'href': './sl-ajax-reload-block-view',
                'data-scale': 'sl_textblock_small',
                'data-imagefloat': 'left'
            }),
            ('imageLeftLarge', {
                'class': 'sl-icon-image-left-large block-server-action',
                'title': translate(
                    _(u'label_float_large_image_left',
                      default=u'Float large image left'),
                    context=self.request),
                'href': './sl-ajax-reload-block-view',
                'data-scale': 'sl_textblock_middle',
                'data-imagefloat': 'left'
            }),
            ('image', {
                'class': 'sl-icon-image block-server-action',
                'title': translate(
                    _(u'label_image_without_floating',
                      default=u'Image without floating'),
                    context=self.request),
                'href': './sl-ajax-reload-block-view',
                'data-scale': 'sl_textblock_large',
                'data-imagefloat': 'no-float'
            }),
            ('imageRightLarge', {
                'class': 'sl-icon-image-right-large block-server-action',
                'title': translate(
                    _(u'label_float_large_image_right',
                      default=u'Float large image right'),
                    context=self.request),
                'href': './sl-ajax-reload-block-view',
                'data-scale': 'sl_textblock_middle',
                'data-imagefloat': 'right'
            }),
            ('imageRight', {
                'class': 'sl-icon-image-right block-server-action',
                'title': translate(
                    _(u'label_float_image_right',
                      default=u'Float image right'),
                    context=self.request),
                'href': './sl-ajax-reload-block-view',
                'data-scale': 'sl_textblock_small',
                'data-imagefloat': 'right'
            }),
            ('cropping', {
                'class': 'sl-icon-crop crop-image',
                'title': translate(
                    _(u'label_crop_image', default='Crop image'),
                    context=self.request),
                'href': './sl-ajax-crop-image'
            }),
        ])
