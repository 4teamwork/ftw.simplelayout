from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.configuration import convert_to_rows
from ftw.simplelayout.interfaces import IPageConfiguration
from ftw.simplelayout.interfaces import ISimplelayoutDefaultSettings
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING
from ftw.testbrowser import browsing
from plone.app.textfield.value import RichTextValue
from plone.registry.interfaces import IRegistry
from plone.uuid.interfaces import IUUID
from unittest2 import TestCase
from zExceptions import BadRequest
from zope.component import getUtility
import json
import transaction


class TestSimplelayoutView(TestCase):

    layer = FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestSimplelayoutView, self).setUp()

        self.contentpage = create(Builder('sl content page'))
        self.page_config = IPageConfiguration(self.contentpage)
        self.url = self.contentpage.absolute_url() + '/@@simplelayout-view'

    @browsing
    def test_render_blocks_not_in_page_configuration(self, browser):
        # Fallback for not saved blocks thru the simplelayout JS lib.
        create(Builder('sl textblock')
               .titled('TextBlock title')
               .within(self.contentpage)
               .having(text=RichTextValue('The text'))
               .having(show_title=True))

        browser.login().visit(self.contentpage, view='@@simplelayout-view')

        self.assertEqual(browser.url, self.url)
        self.assertEquals('TextBlock title',
                          browser.css('.sl-block h2').first.text)

    @browsing
    def test_invalid_simplelayout_save_state_request(self, browser):
        with self.assertRaises(BadRequest):
            browser.login().visit(self.contentpage,
                                  view='sl-ajax-save-state-view',
                                  data={})

    @browsing
    def test_store_save_simplelayout_state_thru_view(self, browser):
        sldata = {"layouts": [1, 1],
                  "blocks": [{"layoutPos": 0,
                              "columnPos": 0,
                              "blockPos": 0,
                              "uid": "uid"},
                             {"layoutPos": 1,
                              "columnPos": 0,
                              "blockPos": 0,
                              "uid": "uid"}]}
        payload = {"data": json.dumps(sldata)}
        browser.login().visit(self.contentpage,
                              view='sl-ajax-save-state-view',
                              data=payload)

        self.assertEquals(convert_to_rows(sldata), self.page_config.load())

    @browsing
    def test_render_blocks_in_different_layouts(self, browser):
        block1 = create(Builder('sl textblock')
                        .titled('Block 1')
                        .within(self.contentpage))
        block2 = create(Builder('sl textblock')
                        .titled('Block 1')
                        .within(self.contentpage))

        self.page_config.store(
            {"layouts": [1, 1],
             "blocks": [{"layoutPos": 0,
                         "columnPos": 0,
                         "blockPos": 0,
                         "uid": IUUID(block1)},
                        {"layoutPos": 1,
                         "columnPos": 0,
                         "blockPos": 0,
                         "uid": IUUID(block2)}]})
        transaction.commit()

        browser.login().visit(self.contentpage)
        self.assertEquals(2,
                          len(browser.css('.sl-layout')),
                          'Expect 2 layouts')

        self.assertEquals(2,
                          len(browser.css('.sl-column.sl-col-1')),
                          'Expect two, one column layouts')

    @browsing
    def test_render_blocks_in_different_columns(self, browser):
        block1 = create(Builder('sl textblock')
                        .titled('Block 1')
                        .within(self.contentpage))
        block2 = create(Builder('sl textblock')
                        .titled('Block 1')
                        .within(self.contentpage))

        self.page_config.store(
            {"layouts": [2],
             "blocks": [{"layoutPos": 0,
                         "columnPos": 0,
                         "blockPos": 0,
                         "uid": IUUID(block1)},
                        {"layoutPos": 0,
                         "columnPos": 1,
                         "blockPos": 0,
                         "uid": IUUID(block2)}]})
        transaction.commit()

        browser.login().visit(self.contentpage)
        self.assertEquals(2,
                          len(browser.css('.sl-column.sl-col-2')),
                          'Expect 2 columns')

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

    @browsing
    def test_show_fallback_view_on_block_render_problems(self, browser):
        textblock = create(Builder('sl textblock')
                           .titled('TextBlock title')
                           .within(self.contentpage)
                           .having(image='Fake image')  # Error while render
                           .having(show_title=False))

        textblock.reindexObject()

        browser.login().visit(self.contentpage)
        self.assertEquals(
            'The block could be rendered. Please check the log for details.',
            browser.css('.sl-block').first.text)
