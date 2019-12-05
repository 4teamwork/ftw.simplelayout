from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.interfaces import IPageConfiguration
from ftw.simplelayout.interfaces import ISimplelayoutDefaultSettings
from ftw.simplelayout.opengraph.interfaces import IOpenGraphDataProvider
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_CONTENT_TESTING
from ftw.testbrowser import browser
from ftw.testbrowser import browsing
from plone import api
from plone.uuid.interfaces import IUUID
from plone.registry.interfaces import IRegistry
from unittest import TestCase
from zope.component import getMultiAdapter
from zope.component import getUtility
import transaction


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
        self.assertOg('og:type', u'website')
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
            IOpenGraphDataProvider, name='opengraph')

        self.assertEquals([], site_root_og().items())

    @browsing
    def test_og_on_simplelayout_page(self, browser):
        page = create(Builder('sl content page').titled(u'\xfc Title'))
        browser.login().visit(page)

        self.assertOg('og:title', page.Title().decode('utf-8'))
        self.assertOg('og:url', page.absolute_url())
        self.assertOg('og:type', u'website')
        self.assertOg('og:image', self.portal.absolute_url() + '/logo.jpg')

    @browsing
    def test_og_image_is_leadimage(self, browser):
        page = create(Builder('sl content page').titled(u'\xfc Title'))
        block = create(Builder('sl textblock').with_dummy_image().within(page))
        self.save_state(page, block)

        # Call page once to cache the image scale
        browser.login().visit(page)

        tag = page.restrictedTraverse('@@leadimage')()
        browser.parse(tag)
        src = browser.css('img').first.attrib['src']

        browser.login().visit(page)
        self.assertOg('og:image', src)

    @browsing
    def test_change_og_type(self, browser):
        self.set_og_type(u'food')
        browser.login().visit()
        self.assertOg('og:type', u'food')

    def set_og_type(self, typename):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISimplelayoutDefaultSettings)
        settings.opengraph_global_type = typename
        transaction.commit()

    def save_state(self, page, block):
        self.page_state = {
            "default": [
                {
                    "cols": [
                        {
                            "blocks": [
                                {
                                    "uid": IUUID(block)
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        page_config = IPageConfiguration(page)
        page_config.store(self.page_state)
        transaction.commit()
