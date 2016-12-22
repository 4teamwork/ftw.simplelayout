from ftw.simplelayout.browser.ajax.utils import json_response
from ftw.simplelayout.utils import get_block_html
from plone.app.textfield.value import RichTextValue
from plone.app.uuid.utils import uuidToObject
from plone.dexterity.utils import addContentToContainer
from plone.dexterity.utils import createContent
from plone.namedfile.file import NamedBlobImage
from plone.uuid.interfaces import IUUID
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


class DnDUpload(BrowserView):

    def __call__(self):
        content = self.request.get('content', None)

        content_created = []
        response = {}

        if content == 'galleryblock':
            contenttype = 'ftw.simplelayout.GallerBlock'
        else:
            # contenttype = 'ftw.simplelayout.TextBlock'
            for item in self.request:
                if item.startswith('file['):
                    content_created.append(
                        self.create_textblock(self.request.get(item)))
                else:
                    raise ValueError('Oh my... you just broke the site')

            if len(content_created) == 1:
                # Insert a single block
                return json_response(
                    self.request,
                    content=get_block_html(content_created[0]),
                    type='singleblock')
            else:
                # Insert multible blocks in layout
                return json_response(
                    self.request,
                    content=get_block_html(content_created[0]),
                    type='singleblock')

    def create_layout_with_blocks(blocks):
        structure = {
            "default": [
                # {
                #     "cols": [
                #         {
                #             "blocks": [
                #                 {
                #                     "uid": "c774b0ca2a5544bf9bb46d865b11bff9"
                #                 }
                #             ]
                #         }
                #     ]
                # }
            ]
        }

        for i, block in enumerate(blocks):
            if i % 2 == 0:
                structure['default'].append(
                    {'cols': [{'blocks': []}]})
            structure['default'][-1]['blocks'].append(
                {'uid': IUUID(block)})

        # return render_layout()

    def create_textblock(self, _file):
        kwargs = {'title': _file.filename,
                  'text': RichTextValue(''),
                  'show_title': False,
                  'image': NamedBlobImage(data=_file.read(),
                                          filename=_file)}
        textblock = createContent('ftw.simplelayout.TextBlock',
                                  **kwargs)
        obj = addContentToContainer(self.context, textblock)
        return obj
