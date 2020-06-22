from ftw.logo.interfaces import IFtwLogo
from ftw.simplelayout.opengraph.og_site_root import PloneRootOpenGraph
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
        """ftw.logo image"""

        return '{}/@@logo/logo/get_logo?r={}'.format(
            api.portal.get().absolute_url(),
            self.get_cache_key()
        )
