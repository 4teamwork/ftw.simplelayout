from ftw.logo.interfaces import IFtwLogo
from ftw.simplelayout.interfaces import ISimplelayout
from ftw.simplelayout.opengraph.og_site_root import PloneRootOpenGraph
from ftw.simplelayout.opengraph.og_sl_page import SimplelayoutPageOpenGraph
from plone import api
from plone.app.caching.interfaces import IETagValue
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import adapts
from zope.component import getMultiAdapter
from zope.interface import Interface


class FtwLogoRootOpenGraph(PloneRootOpenGraph):
    adapts(IPloneSiteRoot, IFtwLogo, Interface)

    def get_cache_key(self):
        adapter = getMultiAdapter((api.portal.get(), self.request),
                                  IETagValue,
                                  name='logo-viewlet')
        return adapter()

    def get_image_url(self):
        """image url"""
        return self.get_ftwlogo_image_url()

    def get_ftwlogo_image_url(self):
        """ftw.logo image"""
        return '{}/@@logo/logo/LOGO?r={}'.format(
            api.portal.get().absolute_url(),
            self.get_cache_key()
        )


class FtwLogoSimplelayoutOpenGraph(SimplelayoutPageOpenGraph, FtwLogoRootOpenGraph):
    adapts(ISimplelayout, IFtwLogo, Interface)

    def get_image_url(self):
        """OG image"""
        leadimage_view = self.context.restrictedTraverse('@@leadimage')

        if leadimage_view.has_image:
            scale = leadimage_view.get_scale()
            return scale and scale.url or ''
        else:
            return self.get_ftwlogo_image_url()
