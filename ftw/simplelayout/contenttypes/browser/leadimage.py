from ftw.simplelayout.contenttypes.contents.interfaces import ITextBlock
from ftw.simplelayout.handlers import unwrap_persistence
from ftw.simplelayout.interfaces import IPageConfiguration
from plone.app.uuid.utils import uuidToObject
from Products.Five.browser import BrowserView
import json
import re


class LeadImageView(BrowserView):
    """Returns the first image of a textblock with image placed in the
    'default' simplelayout container."""

    has_image = None
    block = None

    def __call__(self, scale=None):
        self._get_image()

        scale = scale or self.request.get('scale', 'preview')

        if self.has_image:
            scaler = self.block.restrictedTraverse('@@images')
            return scaler.scale('image', scale=scale, direction="down").tag()
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
