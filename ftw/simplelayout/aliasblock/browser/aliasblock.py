from ftw.simplelayout.browser.blocks.base import BaseBlock
from ftw.simplelayout.browser.provider import SimplelayoutRenderer
from ftw.simplelayout.interfaces import IPageConfiguration
from ftw.simplelayout.interfaces import ISimplelayout
from ftw.simplelayout.utils import get_block_html
from plone import api
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class AliasBlockView(BaseBlock):

    template = ViewPageTemplateFile('templates/aliasblock.pt')

    def __init__(self, context, request):
        super(AliasBlockView, self).__init__(context, request)
        alias = self.context.alias
        self.referenced_obj = alias and alias.to_object or None

    def has_view_permission(self):
        if not self.referenced_obj or self.context.alias.isBroken():
            return False

        return api.user.has_permission('View', obj=self.referenced_obj)

    def can_modify(self):
        return api.user.has_permission('Modify portal content', obj=self.context)

    def referece_is_page(self):
        return ISimplelayout.providedBy(self.referenced_obj)

    def get_referenced_block_content(self):
        """Returns the rendered simplayout content"""
        if self.referece_is_page():
            return self.get_referenced_page_content()
        else:
            return get_block_html(self.referenced_obj)

    def get_referenced_page_content(self):
        page_conf = IPageConfiguration(self.referenced_obj)
        storage = page_conf.load()
        view = self.referenced_obj.restrictedTraverse('view')
        sl_renderer = SimplelayoutRenderer(self.referenced_obj,
                                           storage,
                                           'default',
                                           view=view)
        return sl_renderer.render_layout()
