from ftw.simplelayout.browser.ajax.utils import json_response
from plone.app.uuid.utils import uuidToObject
from plone.uuid.interfaces import IUUID
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zExceptions import BadRequest
import json


class DeleteBlocks(BrowserView):

    confirm_template = ViewPageTemplateFile(
        'templates/block_delete_confirmation.pt')

    def __init__(self, context, request):
        super(DeleteBlocks, self).__init__(context, request)
        self.block = None

    def __call__(self):
        payload = self.request.get('data', None)
        if not payload:
            raise BadRequest('No data given')

        # TODO validate payload contains blocks and confirmed flag.
        data = json.loads(payload)
        self.block = uuidToObject(data['block'])

        self._link_integrity_check()

        if self.request.get('form.submitted', False):
            self.context.manage_delObjects([self.block.id])
            return json_response(self.request, proceed=True)
        else:
            return json_response(self.request,
                                 content=self.confirm_template(),
                                 proceed=False)

    def _link_integrity_check(self):
        pass

    def is_locked_for_current_user(self):
        locking_info = self.block.restrictedTraverse('@@plone_lock_info', None)
        if locking_info:
            return locking_info.is_locked_for_current_user()
        else:
            return False

    @property
    def context_state(self):
        return self.block.restrictedTraverse('@@plone_context_state')

    def block_payload(self):
        block = IUUID(self.block)
        return json.dumps({'block': block})
