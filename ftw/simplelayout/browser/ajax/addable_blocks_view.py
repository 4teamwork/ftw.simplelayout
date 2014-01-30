from zope.publisher.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class AddableBlocks(BrowserView):

    template = ViewPageTemplateFile('templates/addable_blocks.pt')

    def __call__(self):
        return self.template()

    def addable_blocks(self):
        # XXX - Dynamically get block types
        block_types = set(
            ['FileBlock', 'ImageBlock', 'LinkBlock', 'Paragraph'])
        allowed_types = set(self.context.getLocallyAllowedTypes())
        return block_types & allowed_types
