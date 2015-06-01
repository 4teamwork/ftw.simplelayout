from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.interfaces import IPageConfiguration
from ftw.simplelayout.interfaces import ISimplelayoutDefaultSettings
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING
from ftw.simplelayout.testing import SimplelayoutTestCase
from ftw.testbrowser import browsing
from plone.app.textfield.value import RichTextValue
from plone.registry.interfaces import IRegistry
from plone.uuid.interfaces import IUUID
from zExceptions import BadRequest
from zope.component import getUtility
import json
import transaction


class TestSimplelayoutView(SimplelayoutTestCase):

    layer = FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestSimplelayoutView, self).setUp()

        self.contentpage = create(Builder('sl content page'))
        self.page_config = IPageConfiguration(self.contentpage)
        self.url = self.contentpage.absolute_url() + '/@@simplelayout-view'

        self.payload = {
            "default": [
                {
                    "cols": [
                        {
                            "blocks": [
                                {
                                    "uid": "c774b0ca2a5544bf9bb46d865b11bff9"
                                }
                            ]
                        }
                    ]
                },
                {
                    "cols": [
                        {
                            "blocks": [
                                {
                                    "uid": "413fb945952d4403a58ab1958c38f1d2"
                                }
                            ]
                        }
                    ]
                }
            ]
        }

    def test_page_configuration_is_recusrive_persistent(self):
        self.page_config.store(self.payload)

        self.assert_recursive_persistence(self.page_config.load())

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
        payload = {"data": json.dumps(self.payload)}
        browser.login().visit(self.contentpage,
                              view='sl-ajax-save-state-view',
                              data=payload)

        self.assertEquals(self.payload, self.page_config.load())

    @browsing
    def test_render_blocks_in_different_layouts(self, browser):
        block1 = create(Builder('sl textblock')
                        .titled('Block 1')
                        .within(self.contentpage))
        block2 = create(Builder('sl textblock')
                        .titled('Block 1')
                        .within(self.contentpage))

        self.payload['default'][0]['cols'][0]['blocks'][0]['uid'] = IUUID(block1)
        self.payload['default'][1]['cols'][0]['blocks'][0]['uid'] = IUUID(block2)
        self.page_config.store(self.payload)
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

        self.payload['default'][0]['cols'][0]['blocks'][0]['uid'] = IUUID(block1)
        self.payload['default'][1]['cols'][0]['blocks'][0]['uid'] = IUUID(block2)

        # Move Block into layout 1, column 2
        data_colmn = self.payload['default'][1]['cols'][0]
        self.payload['default'].pop()

        self.payload['default'][0]['cols'].append(data_colmn)
        self.page_config.store(self.payload)
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

    @browsing
    def test_empty_sl_page_renders_at_least_one_layout(self, browser):
        browser.login().visit(self.contentpage)

        # By default it's a one column layout.
        self.assertEquals(1,
                          len(browser.css('.sl-column.sl-col-1')),
                          'There should be at least a empty one column layout')
