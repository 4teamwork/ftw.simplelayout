from ftw.simplelayout.contenttypes.contents.interfaces import IGalleryBlock
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

        if self.has_image:
            scale = self.get_scale(scale)
            return scale.tag()
        else:
            return ''

    def get_scale(self, scale=None):
        scale = scale or self.request.get('scale', 'preview')
        scaler = self.block.restrictedTraverse('@@images')
        return scaler.scale('image', scale=scale, direction="down")

    def _get_uids(self):
        page_conf = IPageConfiguration(self.context)
        # look for blocks in default slot first ...
        state_string = json.dumps(unwrap_persistence(
            page_conf.load().get('default', {})))
        # ... then look in all slots.
        state_string += json.dumps(unwrap_persistence(
            page_conf.load()))
        return re.findall(r'\"uid\"\: \"(.+?)\"', state_string)

    def _get_image(self):
        for uid in self._get_uids():
            block = uuidToObject(uid)
            if ITextBlock.providedBy(block) and block.image \
               and block.image.data:
                self.has_image = True
                self.block = block
                return

            if IGalleryBlock.providedBy(block):
                for image in block.listFolderContents({'portal_type': 'Image'}):
                    self.has_image = True
                    self.block = image
                    return
