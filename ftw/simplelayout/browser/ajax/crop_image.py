from Products.Five.browser import BrowserView
from plone.app.uuid.utils import uuidToObject
from zExceptions import BadRequest
import json


class CropImageRedirector(BrowserView):

    def __call__(self):
        payload = self.request.get('data', None)
        if not payload:
            raise BadRequest('No data given')

        data = json.loads(payload)
        block = uuidToObject(data['block'])

        return self.request.RESPONSE.redirect('{0}/image_cropping.json'.format(
            block.absolute_url()))
