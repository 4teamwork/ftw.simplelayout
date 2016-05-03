from ftw.simplelayout.interfaces import ISimplelayoutDefaultSettings
from ftw.simplelayout.opengraph.interfaces import IOpenGraphDataProvider
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_CONTENT_TESTING
from ftw.simplelayout.testing import IS_PLONE_5
from ftw.testbrowser import browser
from ftw.testbrowser import browsing
from plone import api
from plone.registry.interfaces import IRegistry
from unittest2 import skipUnless
from unittest2 import TestCase
from zope.component import getMultiAdapter
from zope.component import getUtility


@skipUnless(not IS_PLONE_5, 'requires plone < 5')
class TestOpenGraph(TestCase):

    layer = FTW_SIMPLELAYOUT_CONTENT_TESTING

    def setUp(self):
        super(TestOpenGraph, self).setUp()

        self.portal = self.layer['portal']

    def assertOg(self, key, value):
        ogvalue = browser.css(
            'meta[property="{0}"]'.format(key)).first.attrib['content']

        self.assertEquals(value, ogvalue)

    @browsing
    def test_og_on_plone_root(self, browser):
        browser.login().visit()

        self.assertOg('og:title', api.portal.get().Title())
        self.assertOg('og:url', self.portal.absolute_url())
        self.assertOg('og:type', 'website')
        self.assertOg('og:image', self.portal.absolute_url() + '/logo.jpg')

    @browsing
    def test_no_og_site_name_on_plone_root(self, browser):
        browser.login().visit()

        self.assertFalse(len(browser.css('meta[property="og:site_name"]')),
                         'Expect no site_name og property on plone root.')

    def test_disable_og_on_plone_root(self):

        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISimplelayoutDefaultSettings)
        settings.opengraph_plone_root = False

        site_root_og = getMultiAdapter(
            (self.portal, self.portal.REQUEST, None),
            IOpenGraphDataProvider)

        self.assertEquals([], site_root_og().items())
