from ftw.simplelayout.interfaces import IBlockModifier
from ftw.simplelayout.interfaces import IBlockProperties
from plone.app.uuid.utils import uuidToObject
from zExceptions import BadRequest
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.publisher.browser import BrowserView
import json


class ReloadBlockView(BrowserView):
    """Reloads a block and performs several modifications before.
    By default it tries to change the view, if the view_name parameter is
    present in the request. Afterwards the BlockReloader adapter gets called,
    which performs block specific modification, like storing image scales.
    Finally the new block html will be returned."""

    def __init__(self, context, request):
        super(ReloadBlockView, self).__init__(context, request)
        self.data = None
        self.block = None
        self.properties = None

    def __call__(self):
        self.data = json.loads(self.request.get('data', "{}"))
        self._get_block()
        self._set_new_view()
        self._block_specific_modifications()
        return self._render_block()

    def _get_block(self):
        uid = self.data.get('uid', None)
        if uid is None:
            raise BadRequest('No uid provided.')

        self.block = uuidToObject(uid)
        self.properties = getMultiAdapter((self.block, self.block.REQUEST),
                                          IBlockProperties)

    def _render_block(self):
        return self.block.restrictedTraverse(
            self.properties.get_current_view_name())()

    def _block_specific_modifications(self):
        modifier = queryMultiAdapter((self.block, self.block.REQUEST),
                                     IBlockModifier)
        if modifier is not None:
            modifier.modify(self.data)

    def _set_new_view(self):
        view_name = self.data.get('view_name', None)
        if view_name is None:
            return

        try:
            self.properties.set_view(view_name.encode('utf-8'))

        except ValueError:
            raise BadRequest(
                'The view "%s" is not available on this block.' % (
                    view_name))

        except RuntimeError:
            raise BadRequest(
                'This object does not support changing the view.')
