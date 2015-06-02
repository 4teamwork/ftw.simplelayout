from ftw.simplelayout.browser.ajax.utils import json_response
from plone.app.uuid.utils import uuidToObject
from plone.dexterity.utils import addContentToContainer
from plone.dexterity.utils import createContent
from plone.rfc822.interfaces import IPrimaryFieldInfo
from plone.uuid.interfaces import IUUID
from zExceptions import BadRequest
from zope.publisher.browser import BrowserView


class FileUpload(BrowserView):
    """Create Files"""

    def __call__(self):
        self.file = self.request.get('file', None)
        self.filename = self.request.get(
            'filename', '').decode('utf-8').lstrip('_')
        self.container_uuid = self.request.get('container_uuid', None)
        self.contenttype = self.request.get('contenttype', None)

        if self.contenttype is None:
            raise BadRequest('No content type provided.')

        if self.file is None:
            raise BadRequest('No content provided.')

        item = self.create()
        return json_response(self.request, uuid=IUUID(item))

    def create(self):
        kwargs = {'title': self.filename}

        container = self.context
        if self.container_uuid:
            container = uuidToObject(self.container_uuid)

        content = createContent(self.contenttype,
                                **kwargs)

        field = IPrimaryFieldInfo(content).field
        value = field._type(data=self.file.read(), filename=self.filename)
        field.set(field.interface(content), value)

        new_obj = addContentToContainer(container, content)

        if self.container_uuid is not None:
            return container
        else:
            return new_obj
