from binascii import a2b_base64
from ftw.simplelayout import _
from ftw.simplelayout.browser.ajax.utils import json_response
from ftw.simplelayout.images.interfaces import IImageLimits
from ftw.simplelayout.interfaces import ISimplelayoutDefaultSettings
from ftw.simplelayout.utils import get_block_html
from plone import api
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.namedfile.field import NamedBlobImage
from plone.namedfile.file import NamedBlobImage as NamedBlobImageFile
from plone.supermodel import model
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.event import notify
from zope.interface import Interface
from zope.interface import provider
from zope.lifecycleevent import ObjectModifiedEvent
import json


class IImageCroppingMarker(Interface):
    """
    """


@provider(IFormFieldProvider)
class IImageCropping(model.Schema):

    model.fieldset('image_cropping',
                   label=_(u'Image cropping'),
                   fields=['use_cropped_image_for_overlay',
                           'cropped_image',
                           'cropped_config'])

    use_cropped_image_for_overlay = schema.Bool(
        title=_(u'use_cropped_image_for_overlay',
                default=u'Use cropped image for overlay'),
        required=False,
        default=True,
        missing_value=True)

    # This field should be hidden. Unfortunately, that's not possible due to a
    # weird bug in the file-selector-widget.
    # If this field is hidden and contains an image, it will raise a validation
    # error on form-save. If we skip the validation of this field, the image will
    # be broken after saving. So, we just hide this field through css.
    #
    # WARNING: This case is not testet. I can't reproduce this issue in the test.
    #
    # form.mode(cropped_config='hidden')
    cropped_image = NamedBlobImage(
        title=_(u'label_cropped_image', default=u'Cropped Image'),
        required=False)

    form.mode(cropped_config='hidden')
    cropped_config = schema.TextLine(
        title=_(u'label_cropped_config', default=u'The final cropped area position and size data'),
        required=False)


class ImageCroppingView(BrowserView):
    template = ViewPageTemplateFile('templates/cropping.pt')
    hard_limit_template = ViewPageTemplateFile('templates/cropping_hard_limit_message.pt')
    soft_limit_template = ViewPageTemplateFile('templates/cropping_soft_limit_message.pt')

    aspect_ratio_configuration = {}

    def __init__(self, context, request):
        super(ImageCroppingView, self).__init__(context, request)
        self._load_aspect_ratio_configuration()
        self.image_limits = IImageLimits(self.context)

    def __call__(self):
        response = {'content': self.template(),
                    'proceed': False}

        if 'form.buttons.save' in self.request.form:
            self.handleSave()
            response['proceed'] = True
            response['content'] = self.get_block_content()

        self.request.response.setHeader("Cache-Control",
                                        "no-cache, no-store, must-revalidate")
        self.request.response.setHeader("Expires", "Sat, 1 Jan 2000 00:00:00 GMT")

        return json_response(self.request, response)

    def handleSave(self):
        is_cropped = json.loads(self.request.form.get('is_cropped', 'false'))

        if is_cropped:
            self.save_cropped_image()
        else:
            self.remove_cropped_image()

        notify(ObjectModifiedEvent(self.context))

    def save_cropped_image(self):
        image_data = self.request.form.get('cropped_image_data')
        config = self.request.form.get('cropped_config')

        contentType, data = self._extract_image_data(image_data)

        self.context.cropped_image = NamedBlobImageFile(
            data=data,
            contentType=contentType,
            filename="abc" + self.context.image.filename)
        self.context.cropped_config = config

    def remove_cropped_image(self):
        self.context.cropped_config = ''
        self.context.cropped_image = None

    def _extract_image_data(self, image_data):
        contentTypePart, dataPart = image_data.split(';')
        key, contentType = contentTypePart.split(':')
        key, data = dataPart.split(',')

        return contentType, a2b_base64(data)

    def aspect_ratios(self):
        return self.aspect_ratio_configuration.get(self.context.portal_type, [])

    def get_block_content(self):
        return get_block_html(self.context)

    def _load_aspect_ratio_configuration(self):
        self.aspect_ratio_configuration = json.loads(
            self._aspect_ratio_configuration_json)

    @property
    def _aspect_ratio_configuration_json(self):
        return api.portal.get_registry_record(
            name='image_cropping_aspect_ratios',
            interface=ISimplelayoutDefaultSettings) or '{}'

    def hard_limit_validation_template(self):
        return self.hard_limit_template()

    def soft_limit_validation_template(self):
        return self.soft_limit_template()

    def config(self):
        return json.dumps({
            'limits': self.limits(),
            'cropped_config': self.cropped_config()
        })

    def cropped_config(self):
        return json.loads(self.context.cropped_config or '{}')

    def limits(self):
        return self.image_limits.get_all_limits_for(self.context.portal_type)
