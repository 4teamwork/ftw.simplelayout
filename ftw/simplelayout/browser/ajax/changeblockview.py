from ftw.simplelayout.interfaces import IBlockConfiguration
from ftw.simplelayout.interfaces import IBlockProperties
from plone.app.uuid.utils import uuidToObject
from zExceptions import BadRequest
from zope.component import getMultiAdapter
from zope.publisher.browser import BrowserView
import json


class ChangeBlockView(BrowserView):
    """Changes the view of a block.
    """

    def __call__(self):
        view_name = self._get_view_name()
        self._set_view_name(view_name)
        return self._render(view_name)

    def _get_view_name(self):
        view_name = self.request.get('view_name', None)
        if view_name is None:
            raise BadRequest('Request parameter "view_name" not found.')
        else:
            return view_name

    def _set_view_name(self, view_name):
        properties = getMultiAdapter((self.context, self.request),
                                     IBlockProperties)

        try:
            properties.set_view(view_name)

        except ValueError:
            raise BadRequest(
                'The view "%s" is not available on this block.' % (
                    view_name))

        except RuntimeError:
            raise BadRequest(
                'This object does not support changing the view.')

    def _render(self, view_name):
        return self.context.restrictedTraverse('@@' + view_name)()


class ReloadBlockView(BrowserView):
    """Reloads the block view"""

    def __call__(self):
        data = json.loads(self.request.get('data', {}))
        uuid = data.get('uid', None)

        if uuid is None:
            raise BadRequest('No uid provided.')

        block = uuidToObject(uuid)

        #TODO Image scale handling - should be placed in a TextBlock specific
        # reload block view
        image_scale = data.get('scale', None)
        conf = IBlockConfiguration(block)
        blockconf = conf.load()

        if image_scale:
            blockconf['scale'] = image_scale
            conf.store(blockconf)  # necessary?

        properties = getMultiAdapter((block, block.REQUEST),
                                     IBlockProperties)
        return block.restrictedTraverse(
            properties.get_current_view_name())()
