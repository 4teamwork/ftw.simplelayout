from AccessControl.requestmethod import postonly
from ftw.simplelayout import _
from ftw.simplelayout.browser.ajax.utils import json_error_responses
from ftw.simplelayout.browser.ajax.utils import json_response
from ftw.simplelayout.utils import IS_PLONE_5
from plone import api
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import iterSchemataForType
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from zExceptions import BadRequest
from zope.component import getUtility
from zope.i18n import translate
import os.path

if IS_PLONE_5:
    from plone.namedfile.utils import getImageInfo
else:
    # Plone 4
    from plone.namedfile.file import getImageInfo


class DropzoneUploadBase(BrowserView):

    @json_error_responses
    @postonly
    def __call__(self, REQUEST):
        self.validate_payload()
        obj = self.create(self.request.get('file'))
        return self.created_response(obj)

    def validate_payload(self):
        if 'file' not in self.request.form:
            raise BadRequest('Missing field "file".')

    def created_response(self, obj):
        self.request.response.setStatus(201)
        return json_response(self.request,
                             content='Created',
                             proceed=True,
                             url=obj.absolute_url())

    def is_dexterity_fti(self, portal_type):
        portal_types = getToolByName(self.context, 'portal_types')
        return IDexterityFTI.providedBy(portal_types.get(portal_type))

    def create_obj(self, portal_type, file_field_name, file_):
        filename = safe_unicode(os.path.basename(file_.filename))
        kwargs = {'container': self.context,
                  'type': portal_type,
                  'title': self.request.get('title', filename),
                  'description': self.request.get('description'),
                  'safe_id': True}

        if self.is_dexterity_fti(portal_type):
            field = self.get_field_of_type(portal_type, file_field_name)
            kwargs[file_field_name] = field._type(file_, filename=filename)
            return api.content.create(**kwargs)

        else:
            obj = api.content.create(**kwargs)
            obj.Schema().getField(file_field_name).set(obj, file_)
            obj.reindexObject(idxs=['SearchableText'])
            return obj

    def get_field_of_type(self, portal_type, file_field_name):
        for schema in iterSchemataForType(portal_type):
            if file_field_name in schema:
                return schema[file_field_name]


class FileListingUpload(DropzoneUploadBase):

    def create(self, file_):
        return self.create_obj(self.get_upload_portal_type(), 'file', file_)

    def get_upload_portal_type(self):
        context_fti = getUtility(IDexterityFTI, name=self.context.portal_type)

        if context_fti.allowed_content_types:
            return context_fti.allowed_content_types[0]
        else:
            return 'File'


class GalleryUpload(DropzoneUploadBase):

    def create(self, file_):
        content_type, width, height = getImageInfo(file_.read())
        file_.seek(0)
        if not content_type:
            error = translate(_('Only images can be added to the gallery.'), context=self.request)
            raise BadRequest(error)

        return self.create_obj('Image', 'image', file_)
