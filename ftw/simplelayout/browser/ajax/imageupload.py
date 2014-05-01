from plone.app.textfield.value import RichTextValue
from plone.dexterity.utils import addContentToContainer
from plone.dexterity.utils import createContent
from plone.namedfile.file import NamedBlobImage
from plone.uuid.interfaces import IUUID
from zExceptions import BadRequest
from zope.publisher.browser import BrowserView
import json


class ImageUpload(BrowserView):
    """Creates a textblick with an image"""

    def __call__(self):
        self.image = self.request.get('image', None)
        self.filename = self.request.get(
            'filename', '').decode('utf-8').lstrip('_')

        if self.image is None:
            raise BadRequest('No image provided.')

        item = self.create()
        return json.dumps({'uuid': IUUID(item)})

    def create(self):
        kwargs = {
                  'title': self.filename,
                  'text': RichTextValue(''),
                  'show_title': False,
                  'image': NamedBlobImage(data=self.image.read(),
                                          filename=self.filename)}
        textblock = createContent('ftw.simplelayout.TextBlock',
                                  **kwargs)
        obj = addContentToContainer(self.context, textblock)
        return obj
