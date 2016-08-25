from collections import OrderedDict
from ftw.simplelayout.interfaces import ISimplelayout
from ftw.simplelayout.opengraph.og_site_root import PloneRootOpenGraph
from plone import api
from zope.component import adapts
from zope.interface import Interface


class SimplelayoutPageOpenGraph(PloneRootOpenGraph):
    adapts(ISimplelayout, Interface, Interface)

    def __call__(self):
        """Returns a dict with all og:key, value"""

        return OrderedDict([
            ('og:title', self.get_title()),
            ('og:type', self.get_type()),
            ('og:url', self.get_url()),
            ('og:image', self.get_image_url())
        ])

    def get_title(self):
        """OG Title"""
        return self.context.title_or_id()

    def get_url(self):
        """OG url"""
        return self.context.absolute_url().decode('utf-8')

    def get_image_url(self):
        """OG image"""
        leadimage_view = self.context.restrictedTraverse('@@leadimage')
        if leadimage_view.has_image:
            scale = leadimage_view.get_scale()
            return scale and scale.url or ''
        else:
            return super(SimplelayoutPageOpenGraph, self).get_image_url()

    def get_site_name(self):
        """OG site name"""
        return api.portal.get().Title().decode('utf-8')
