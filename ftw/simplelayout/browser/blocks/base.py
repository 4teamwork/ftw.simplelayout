from plone.uuid.interfaces import IUUID
from Products.Five.browser import BrowserView


SL_BLOCK_WRAPPER = """<div class="sl-block-content" data-uid="{uid}">
{content}</div>"""


class BaseBlock(BrowserView):

    def __call__(self):
        return SL_BLOCK_WRAPPER.format(**dict(uid=self.get_uid(),
                                              content=self.template()))

    def get_uid(self):
        return IUUID(self.context)
