from plone.app.textfield.value import RichTextValue
from plone.dexterity.utils import addContentToContainer
from plone.dexterity.utils import createContent
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.namedfile.file import NamedBlobImage
from plone.uuid.interfaces import IUUID
from zExceptions import BadRequest
from zope.component import getUtility
from zope.container.interfaces import INameChooser
from zope.publisher.browser import BrowserView
import json


class ImageUpload(BrowserView):
    """Creates a textblick with an image"""

    def __call__(self):
        self.image = self.request.get('image', None)
        self.filename = self.request.get('filename', '').decode('utf-8')

        if self.image is None:
            raise BadRequest('No image provided.')

        item = self.create()
        return json.dumps({'uuid': IUUID(item)})

    def create(self):
        kwargs = {'title': self.filename,
                  'text': RichTextValue(''),
                  'show_title': False,
                  'image': NamedBlobImage(data=self.image.read(),
                                          filename=self.filename)}
        textblock = createContent('ftw.simplelayout.TextBlock',
                                  **kwargs)
        obj = addContentToContainer(self.context, textblock)
        return obj

    def generate_id(self):
        normalizer = getUtility(IIDNormalizer)
        chooser = INameChooser(self.context)

        normalized = normalizer.normalize(self.filename)
        normalized = normalized.replace('_', '-').replace(' ', '-').lower()

        return chooser.chooseName(normalized, self.context)
