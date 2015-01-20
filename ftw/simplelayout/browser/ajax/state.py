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
        ...        "position": 0
        ...    }, {
        ...        "height": "100px",
        ...        "layout": 1,
        ...        "column": 1,
        ...        "position": 0
        ...    }],
        ...    "layouts": [2, 4]
        ...}
    """

    def __call__(self):
        payload = self._get_payload()
        payload = self._load_objects(payload)
        self._update_order(payload)
        self._update_positions_and_sizes(payload)
        self._update_slot_information(payload)

        return json.dumps(
            {'Status': 'OK',
             'msg': 'Saved state of {0} blocks'.format(len(payload))})

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

        for item in payload:
            item['obj'] = uuid_to_object[item['uuid']]

        return payload

    def _update_order(self, payload):
        ids = [item.get('obj').getId() for item in payload]
        self.context.moveObjectsByDelta(ids, -len(ids))

        # Position of not updated objects may have changed, so we reindex
        # all children of the current context.
        for child in self.context.objectValues():
            child.reindexObject(idxs=['getObjPositionInParent'])

    def _update_positions_and_sizes(self, payload):
        for item in payload:
            display = getMultiAdapter((item['obj'], self.request),
                                      IDisplaySettings)
            display.set_position(item['position'])
            display.set_size(item['size'])
            display.set_image_styles(item['imagestyles'])

    def _update_slot_information(self, payload):
        for item in payload:
            set_slot_information(item['obj'], item['slot'])
