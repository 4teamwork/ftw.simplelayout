from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.interfaces import IPageConfiguration
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING
from ftw.simplelayout.testing import SimplelayoutTestCase
from ftw.testbrowser import browsing
from zExceptions import BadRequest
import json


class TestLayoutReloadView(SimplelayoutTestCase):

    layer = FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.setup_sample_ftis(self.portal)
        self.setup_block_views()
        self.content = create(Builder('sample container'))

    def test_layout_reload_view_needs_slot_name_and_layoutindex(self):
        with self.assertRaises(BadRequest):
            self.content.restrictedTraverse('@@sl-ajax-reload-layout-view')()

        payload = json.dumps({'name': 'default', 'layoutindex': '0'})
        self.portal.REQUEST.set('data', payload)
        response = json.loads(self.content.restrictedTraverse(
            '@@sl-ajax-reload-layout-view')())

        self.assertIn('content', response)

    @browsing
    def test_layout_reload_view_renders_layout_without_wrapper(self, browser):
        payload = json.dumps({'name': 'default', 'layoutindex': '0'})
        self.portal.REQUEST.set('data', payload)
        response = json.loads(self.content.restrictedTraverse(
            '@@sl-ajax-reload-layout-view')())

        browser.open_html(response['content'])

        self.assertFalse(browser.css('.sl-layout'),
                         'Expect no sl-layout wrapper')

    @browsing
    def test_column_has_empty_config_by_default(self, browser):
        payload = json.dumps({'name': 'default', 'layoutindex': '0'})
        self.portal.REQUEST.set('data', payload)
        response = json.loads(self.content.restrictedTraverse(
            '@@sl-ajax-reload-layout-view')())

        browser.open_html(response['content'])

        self.assertEquals(
            '{}', browser.css('.sl-layout-content').first.attrib['data-config']
        )

    @browsing
    def test_render_store_layout_configuration_in_state(self, browser):
        config = IPageConfiguration(self.content)
        state = {
            "default": [
                {"cols": [{"blocks": []}]},
                {"cols": [{"blocks": []}]}
            ]
        }
        config.store(state)

        configdata = {'somekey': 'somevalue'}
        payload = json.dumps({'name': 'default',
                              'layoutindex': '1',
                              'config': configdata})
        self.portal.REQUEST.set('data', payload)
        response = json.loads(self.content.restrictedTraverse(
            '@@sl-ajax-reload-layout-view')())

        browser.open_html(response['content'])

        self.assertDictEqual(
            configdata,
            json.loads(
                browser.css('.sl-layout-content').first.attrib['data-config']))
        self.assertTrue(browser.css('.sl-layout-content.somevalue'),
                        'Expect one item')
