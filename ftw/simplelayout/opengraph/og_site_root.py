from collections import OrderedDict
from ftw.simplelayout.interfaces import ISimplelayoutDefaultSettings
from ftw.simplelayout.opengraph.interfaces import IOpenGraphDataProvider
from plone import api
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import adapts
from zope.component import getUtility
from zope.interface import implements
from zope.interface import Interface


class PloneRootOpenGraph(object):
    implements(IOpenGraphDataProvider)
    adapts(IPloneSiteRoot, Interface, Interface)

    def __init__(self, context, request, view):
        """adapts context and request and view"""
        self.context = context
        self.request = request
        self.view = view

    def __call__(self):
        """Returns a dict with all og:key, value"""

        if self._settings.opengraph_plone_root:
            return OrderedDict([
                ('og:title', self.get_title()),
                ('og:type', self.get_type()),
                ('og:url', self.get_url()),
                ('og:image', self.get_image_url()),
                ('og:description', self.get_description()),
                ('fb:app_id', self.get_fb_app_id()),
                ('fb:admins', self.get_fb_admins()),
            ])
        else:
            return OrderedDict([])

    @property
    def _settings(self):
        registry = getUtility(IRegistry)
        return registry.forInterface(
            ISimplelayoutDefaultSettings, check=False)

    def _escape(self, text):
        """More or less taken from https://wiki.python.org/moin/EscapingHtml
        """
        html_escape_table = OrderedDict([
            ("&", "&amp;"),
            ('"', "&quot;"),
            ("'", "&apos;"),
            (">", "&gt;"),
            ("<", "&lt;"),
        ])

        for sign in html_escape_table.items():
            text = text.replace(*sign)
        return text

    def get_title(self):
        """OG Title"""
        return self._escape(api.portal.get().Title().decode('utf-8'))

    def get_type(self):
        """OG type"""

        return self._settings.opengraph_global_type

    def get_url(self):
        """OG url"""
        return api.portal.get().absolute_url().decode('utf-8')

    def get_image_url(self):
        """OG image"""
        return api.portal.get().absolute_url() + '/logo.jpg'

    def get_site_name(self):
        """OG site name"""
        return None

    def get_description(self):
        """OG description"""
        return self._escape(api.portal.get().Description().decode('utf-8'))

    def get_fb_app_id(self):
        """FB app ID"""
        return self._settings.facebook_app_id

    def get_fb_admins(self):
        """FB admins"""
        return self._settings.facebook_admins
