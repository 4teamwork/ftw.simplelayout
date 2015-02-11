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

    def __call__(self):
        payload = self.request.get('data', None)
        if not payload:
            raise BadRequest('No data given')

        # TODO validate payload contains blocks and confirmed flag.
        data = json.loads(payload)
        blocks = [uuidToObject(uid) for uid in data['blocks']]

        if data['confirmed']:
            ids = []
            for block in blocks:
                ids.append(block.id)

            with DisbaledLinkIntegrityCheck(self.request):
                self.context.manage_delObjects(ids)
            msg = ''
        else:
            infos = []
            for block in blocks:
                info = LinkIntegrityInfo(block)
                if info:
                    infos.append(info)
            if infos:
                msg = {'msg': 'The following blocks has references: {0}'.format(
                    ','.join(infos))}
            else:
                msg = {'msg': 'Delete the selected block(s)?'}
        return json.dumps(msg)
