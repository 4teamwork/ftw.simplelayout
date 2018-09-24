from Acquisition import aq_chain
from binascii import a2b_base64
from ftw.simplelayout.browser.ajax.utils import json_response
from ftw.simplelayout.images.configuration import Configuration
from ftw.simplelayout.images.interfaces import IImageLimits
from ftw.simplelayout.interfaces import ISimplelayoutBlock
from ftw.simplelayout.utils import get_block_html
from plone.namedfile.file import NamedBlobImage as NamedBlobImageFile
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
import json


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
        # It's possible, that we're cropping an image within a block instead an
        # image of a block. In this case, we're not able to return the sl-block
        # html. To fix this issue, we're looking up the next sl-block.
        #
        # This case happens i.e. while cropping a slider pane within the sliderblock.
        return get_block_html(self._sl_block())

    def _load_aspect_ratio_configuration(self):
        self.aspect_ratio_configuration = Configuration().aspect_ratios()

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
        return self.image_limits.get_all_limits()

    def _sl_block(self):
        for obj in aq_chain(self.context):
            if ISimplelayoutBlock.providedBy(obj):
                return obj

        raise AttributeError('No simplelayout block in aq_chain')
