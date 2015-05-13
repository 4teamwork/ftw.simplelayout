from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.interfaces import ISimplelayoutDefaultSettings
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING
from ftw.testbrowser import browsing
from plone.app.textfield.value import RichTextValue
from plone.registry.interfaces import IRegistry
from unittest2 import TestCase
from zope.component import getUtility
import transaction


class TestSimplelayoutView(TestCase):

    layer = FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestSimplelayoutView, self).setUp()

        self.contentpage = create(Builder('sl content page'))
        self.url = self.contentpage.absolute_url() + '/@@simplelayout-view'

    @browsing
    def test_view_renders(self, browser):
        textblock = create(Builder('sl textblock')
                           .titled('TextBlock title')
                           .within(self.contentpage)
                           .having(text=RichTextValue('The text'))
                           .having(show_title=False))

        textblock.reindexObject()

        browser.login().visit(self.contentpage, view='@@simplelayout-view')

        self.assertEqual(browser.url, self.url)
        self.assertEquals('The text', browser.css(
            '.sl-block').first.text)
        self.assertFalse(len(browser.css('.sl-block-content h2')))

        textblock.show_title = True
        transaction.commit()

        browser.visit(self.contentpage)
        self.assertEquals('TextBlock title',
                          browser.css('.sl-block h2').first.text)

    @browsing
    def test_simplelayout_default_config_from_control_panel(self, browser):
        browser.login().visit(self.contentpage, view='@@simplelayout-view')

        data_attr_value = browser.css(
            '[data-sl-settings]').first.attrib['data-sl-settings']
        self.assertEquals('{}',
                          data_attr_value,
                          'Expect an empty dict')

        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISimplelayoutDefaultSettings)
        settings.slconfig = u'{"layouts": [1, 2]}'
        transaction.commit()

        browser.login().visit(self.contentpage, view='@@simplelayout-view')
        data_attr_value = browser.css(
            '[data-sl-settings]').first.attrib['data-sl-settings']

        self.assertEquals(u'{"layouts": [1, 2]}',
                          data_attr_value,
                          'Expect the layout setting in default config.')

    # @browsing
    # def test_show_fallback_view_on_block_render_problems(self, browser):
    #     textblock = create(Builder('sl textblock')
    #                        .titled('TextBlock title')
    #                        .within(self.contentpage)
    # .having(image='Fake image') # Error while render
    #                        .having(show_title=False))

    #     textblock.reindexObject()

    #     browser.login().visit(self.contentpage)
    #     self.assertEquals(
    #         'The block could be rendered. Please check the log for details.',
    #         browser.css('.sl-block').first.text)
