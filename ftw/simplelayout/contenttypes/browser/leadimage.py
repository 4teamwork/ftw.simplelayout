from ftw.simplelayout.contenttypes.contents.interfaces import ITextBlock
from ftw.simplelayout.handlers import unwrap_persistence
from ftw.simplelayout.interfaces import IPageConfiguration
from plone.app.uuid.utils import uuidToObject
from plone.memoize import ram
from Products.Five.browser import BrowserView
import hashlib
import json
import re


def _render_cachkey(method, self):
    key = (str(self.context.modified().millis()),
           self.request.get('scale', ''),
           __name__ + method.__name__)
    return hashlib.md5(';'.join(key)).hexdigest()


class LeadImageView(BrowserView):
    """Returns the first image of a textblock with image placed in the
    'default' simplelayout container."""

    has_image = None
    block = None

    @ram.cache(_render_cachkey)
    def __call__(self):
        self._get_image()

        scale = self.request.get('scale', 'mini')

        if self.has_image:
            scaler = self.block.restrictedTraverse('@@images')
            return scaler.scale('image', scale=scale).tag()
        else:
            return ''

    def _get_uids(self):
        page_conf = IPageConfiguration(self.context)
        state_string = json.dumps(unwrap_persistence(
            page_conf.load().get('default', {})))

        return re.findall(r'\"uid\"\: \"(.+?)\"', state_string)

    def _get_image(self):
        for uid in self._get_uids():
            block = uuidToObject(uid)
            if ITextBlock.providedBy(block) and block.image \
               and block.image.data:
                self.has_image = True
                self.block = block
                break
