from Products.CMFPlone.utils import isLinked
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.uuid.utils import uuidToObject
from plone.uuid.interfaces import IUUID
from zExceptions import BadRequest
import json

import logging

logger = logging.getLogger("Plone")

class DeleteBlocks(BrowserView):

    confirm_template = ViewPageTemplateFile(
        'templates/block_delete_confirmation.pt')

    def __init__(self, context, request):
        super(DeleteBlocks, self).__init__(context, request)
        # TODO - Implement deleting of multiple blocks
        self.block = None

    def __call__(self):
        payload = self.request.get('data', None)
        logger.info("Delete Block");
        if not payload:
            raise BadRequest('No data given')

        # TODO validate payload contains blocks and confirmed flag.
        data = json.loads(payload)
        self.block = uuidToObject(data['blocks'][0])

        self._link_integrity_check()

        if self.request.get('form.submitted', False):
            self.context.manage_delObjects([self.block.id])
        else:
            return json.dumps(dict(
                content=self.confirm_template(),
                proceed=False,
            ))
        return json.dumps(dict(
            proceed=True,
        ))

    def _link_integrity_check(self):
        pass
        #isLinked(self.block)

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
        blocks = [IUUID(self.block)]
        return json.dumps({'blocks': blocks})

