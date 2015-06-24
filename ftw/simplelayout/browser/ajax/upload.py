from ftw.simplelayout.browser.ajax.utils import json_response
from plone.app.uuid.utils import uuidToObject
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zExceptions import BadRequest
import json


class UploadForm(BrowserView):

    template = ViewPageTemplateFile('templates/upload.pt')

    _finished_edit = False

    def __call__(self):
        payload = self.request.get('data', None)
        if not payload:
            raise BadRequest('No data given')

        data = json.loads(payload)
        self.block = uuidToObject(data['block'])

        return self.render()

    def get_upload_url(self):
        """
        return upload url in current folder
        """
        ploneview = self.block.restrictedTraverse('@@plone')
        folder_url = ploneview.getCurrentFolderUrl()
        return '%s/@@quick_upload' % folder_url

    def render(self):
        response = {'content': self.template(),
                    'proceed': False}

        if self._finished_edit:
            response['proceed'] = True
            response['content'] = self.context()
        return json_response(self.request, response)
