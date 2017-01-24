from ftw.simplelayout.browser.ajax.utils import json_response
from ftw.simplelayout.browser.provider import SimplelayoutRenderer
from ftw.simplelayout.interfaces import IBlockConfiguration
from ftw.simplelayout.interfaces import IPageConfiguration
from plone import api
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

    def __init__(self, context, request):
        super(DnDUpload, self).__init__(context, request)
        self.contenttype = self.request.get('contenttype', None)
        self.name = self.request.get('name', None)
        self.columns = self.request.get('columns', None)

    def __call__(self):
        content_created = []
        response = {}

        if self.contenttype == 'galleryblock':
            galleryblock = self.create_gallerblock()
            for param, value in self.request.items():
                if param.startswith('file['):
                    self.add_image_to_gallery(galleryblock, value)
            content_created.append(galleryblock)

        else:
            for param, value in self.request.items():
                if param.startswith('file['):
                    content_created.append(
                        self.create_textblock(value))

        response['content'] = self.create_layout_with_blocks(content_created)
        return json_response(self.request, response)

    def create_layout_with_blocks(self, blocks):
        storage = {
            "tmp": [
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
            if i % int(self.columns) == 0:
                storage['tmp'].append(
                    {'cols': []})

            storage['tmp'][-1]['cols'].append(
                {'blocks': [
                    {
                        'uid': IUUID(block)
                    }
                ]}
            )

        conf = IPageConfiguration(self.context)
        data = conf.load()
        # Instert layouts from storage in position 0
        data[self.name][0:0] = storage.get('tmp')
        conf.store(data)

        sl_renderer = SimplelayoutRenderer(
            self.context, storage, 'tmp', view=self)
        return sl_renderer.render_layout()

    def create_textblock(self, _file):
        filename = _file.filename.decode('utf-8')
        kwargs = {'title': filename,
                  'text': RichTextValue(''),
                  'show_title': False,
                  'image': NamedBlobImage(data=_file.read(),
                                          filename=filename)}
        textblock = createContent('ftw.simplelayout.TextBlock',
                                  **kwargs)
        obj = addContentToContainer(self.context, textblock)
        config = IBlockConfiguration(obj)
        data = config.load()
        data['scale'] = 'sl_textblock_large'
        data['imagefloat'] = 'no-float'
        config.store(data)

        return obj

    def create_gallerblock(self):
        # XXX: Implement title
        kwargs = {}
        galleryblock = createContent('ftw.simplelayout.GalleryBlock',
                                     **kwargs)
        obj = addContentToContainer(self.context, galleryblock)
        return obj

    def add_image_to_gallery(self, galleryblock, _file):
        filename = _file.filename.decode('utf-8')
        kwargs = {'title': filename,
                  'text': RichTextValue(''),
                  'show_title': False,
                  'image': _file}

        api.content.create(container=galleryblock,
                           type='Image',
                           safe_id=True,
                           **kwargs)
