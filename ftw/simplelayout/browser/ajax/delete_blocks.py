from plone.app.linkintegrity.info import LinkIntegrityInfo
from plone.app.uuid.utils import uuidToObject
from Products.Five.browser import BrowserView
from zExceptions import BadRequest
import json


class DisbaledLinkIntegrityCheck(object):

    """Disables LinkIntegritry check """

    def __init__(self, request):
        self.request = request

    def __enter__(self):
        self.request.environ['link_integrity_info'] = 'all'

    def __exit__(self, _exc_type, _exc_value, _traceback):
        del self.request.environ['link_integrity_info']


class DeleteBlocks(BrowserView):

    def __init__(self, context, request):
        super(DeleteBlocks, self).__init__(context, request)
        self.blocks = None

    def __call__(self):
        payload = self.request.get('data', None)
        if not payload:
            raise BadRequest('No data given')

        # TODO validate payload contains blocks and confirmed flag.
        data = json.loads(payload)
        self.blocks = [uuidToObject(uid) for uid in data['blocks']]

        msg = self._link_integrity_check()

        if data.get('confirmed', False):
            ids = []
            for block in self.blocks:
                ids.append(block.id)

            with DisbaledLinkIntegrityCheck(self.request):
                self.context.manage_delObjects(ids)
            msg = ''
        return json.dumps(msg)

    def _link_integrity_check(self):
        # TODO - Implement link integrity check.
        return {'msg': 'Delete the selected block(s)'}
