from ftw.simplelayout.browser.ajax.utils import json_response
from ftw.simplelayout.images.cropping.behaviors import IImageCropping
from ftw.simplelayout.interfaces import ISimplelayoutBlock
from ftw.simplelayout.utils import get_block_html
from plone.app.uuid.utils import uuidToObject
from plone.dexterity.browser.edit import DefaultEditForm
from plone.dexterity.events import EditCancelledEvent
from plone.dexterity.events import EditFinishedEvent
from plone.dexterity.i18n import MessageFactory as _
from plone.dexterity.interfaces import IDexterityEditForm
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form import button
from zExceptions import BadRequest
from zope.event import notify
from zope.interface import classImplements
import json


class BlockEditRedirector(BrowserView):

    def __call__(self):
        payload = self.request.get('data', None)
        if not payload:
            raise BadRequest('No data given')

        data = json.loads(payload)
        block = uuidToObject(data['block'])

        return self.request.RESPONSE.redirect('{0}/edit.json'.format(
            block.absolute_url()))


class EditForm(DefaultEditForm):
    template = ViewPageTemplateFile('templates/edit_block_form.pt')

    _finished_edit = False

    @button.buttonAndHandler(_(u'Save'), name='save')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        if IImageCropping.providedBy(self.context) and \
                self.context.image is not data.get('image'):
            data['IImageCropping.cropped_config'] = None
            data['IImageCropping.cropped_image'] = None

        self.applyChanges(data)
        notify(EditFinishedEvent(self.context))

        self._finished_edit = True

    @button.buttonAndHandler(_(u'Cancel'), name='cancel')
    def handleCancel(self, action):
        notify(EditCancelledEvent(self.context))

    def get_block_content(self):
        return get_block_html(self.context)

    def render(self):

        response = {'content': self.template(),
                    'proceed': False}

        if self._finished_edit:
            response['proceed'] = True
            response['content'] = self.get_block_content()

        self.request.response.setHeader("Cache-Control",
                                        "no-cache, no-store, must-revalidate")
        self.request.response.setHeader("Expires", "Sat, 1 Jan 2000 00:00:00 GMT")

        return json_response(self.request, response)

classImplements(EditForm, IDexterityEditForm)


class InnerEditRedirector(BrowserView):

    def __call__(self):
        payload = self.request.get('data', None)
        if not payload:
            raise BadRequest('No data given')

        data = json.loads(payload)
        block = uuidToObject(data['uid'])

        return self.request.RESPONSE.redirect('{0}/inner_edit.json'.format(
            block.absolute_url()))


class InnerEditForm(EditForm):
    """Edit form for items in a folderish block"""

    def get_block_content(self):
        block = self.context.aq_parent
        if ISimplelayoutBlock.providedBy(block):
            return get_block_html(block)
        else:
            raise ValueError("The parent needs to be a simplelayout block")


classImplements(InnerEditForm, IDexterityEditForm)
