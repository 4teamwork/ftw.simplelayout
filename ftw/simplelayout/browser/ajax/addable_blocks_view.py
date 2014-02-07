from Products.CMFPlone.interfaces.constrains import ISelectableConstrainTypes
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.publisher.browser import BrowserView


class AddableBlocks(BrowserView):

    template = ViewPageTemplateFile('templates/addable_blocks.pt')

    def __call__(self):
        return self.template()

    def addable_blocks(self):
        # XXX - Dynamically get block types
        block_types = set(
            ['ftw.simplelayout.TextBlock'])
        allowed_types = set(ISelectableConstrainTypes(
            self.context).getImmediatelyAddableTypes())
        return block_types & allowed_types
