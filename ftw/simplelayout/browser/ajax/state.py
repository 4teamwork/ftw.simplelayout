from ftw.simplelayout.interfaces import IDisplaySettings
from ftw.simplelayout.slot import set_slot_information
from plone.uuid.interfaces import IUUID
from zExceptions import BadRequest
from zope.component import getMultiAdapter
from zope.publisher.browser import BrowserView
import json


class SaveStateView(BrowserView):

    """Updates the state of the blocks in the current context.
    Expects a "payload" parameter in the request with json list of
    block states and the total amount of columns of each layout.

    Example:

    >>> payload ={
        ...    "blocks", [{
        ...        "height": "100px",
        ...        "layout": 0,
        ...        "column": 3,
        ...        "position": 0,
        ...        "uid": 122345678
        ...    }, {
        ...        "height": "100px",
        ...        "layout": 1,
        ...        "column": 1,
        ...        "position": 0,
        ...        "uid": 122345678
        ...    }],
        ...    "layouts": [2, 4]
        ...}
    """

    def __call__(self):
        payload = self._get_payload()
        payload = self._load_objects(payload)
        self._update(payload)

        return json.dumps(
            {'Status': 'OK',
             'msg': 'Saved state of {0} blocks'.format(
                 len(payload['blocks']))})

    def _get_payload(self):
        payload = self.request.get('payload', None)
        if payload is None:
            raise BadRequest('Request parameter "payload" not found.')
        else:
            return json.loads(payload)

    def _load_objects(self, payload):
        # loads the objects into the payload
        uuid_to_object = {}
        for obj in self.context.listFolderContents():
            uuid_to_object[IUUID(obj)] = obj

        for item in payload['blocks']:
            item['obj'] = uuid_to_object[item['uid']]

        return payload

    def _update(self, payload):
        for idx, item in enumerate(payload['blocks']):
            display = getMultiAdapter((item['obj'], self.request),
                                      IDisplaySettings)
            display.set_position(item['position'])
            display.set_height(item['height'])
            display.set_layout(item['layout'])
            display.set_column(item['column'])

            total_columns = payload['layouts'][item['layout']]
            display.set_total_columns(total_columns)
