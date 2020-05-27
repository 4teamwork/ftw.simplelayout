from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ftw.simplelayout.browser.blocks.base import BaseBlock
from ftw.simplelayout.interfaces import ISimplelayoutBlock
from zExceptions import Unauthorized


try:
    from ftw.slider.interfaces import IContainer
except ImportError:
    class IContainer(object):
        """Dummy class if ftw.slider isn't installed.
        """


class AliasBlockView(BaseBlock):

    template = ViewPageTemplateFile('templates/aliasblock.pt')

    def __init__(self, context, request):
        super(AliasBlockView, self).__init__(context, request)
        self.referenced_page = self.context.alias.to_object

    def get_referenced_block_content(self):
        """Returns the rendered simplayout block"""
        try:
            if ISimplelayoutBlock.providedBy(self.referenced_page):
                view = self.referenced_page.restrictedTraverse('@@block_view')
                return view.template()
            elif IContainer.providedBy(self.referenced_page):
                view = self.referenced_page.restrictedTraverse('@@slider_view')
                return view.template()
        except Unauthorized:
            return
