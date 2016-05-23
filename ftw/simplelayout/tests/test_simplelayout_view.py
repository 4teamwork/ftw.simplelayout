from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.browser.simplelayout import SimplelayoutView
from ftw.simplelayout.interfaces import IBlockProperties
from ftw.simplelayout.interfaces import IPageConfiguration
from ftw.simplelayout.interfaces import ISimplelayoutContainerConfig
from ftw.simplelayout.interfaces import ISimplelayoutDefaultSettings
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING
from ftw.simplelayout.testing import SimplelayoutTestCase
from ftw.simplelayout.tests.sample_types import ISampleSimplelayoutContainer
from ftw.testbrowser import browsing
from plone.app.textfield.value import RichTextValue
from plone.registry.interfaces import IRegistry
from plone.uuid.interfaces import IUUID
from zExceptions import BadRequest
from zExceptions import Unauthorized
from zope.component import getGlobalSiteManager
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import provideAdapter
from zope.interface import implements
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserView
import json
import transaction


class TestSimplelayoutView(SimplelayoutTestCase):

    layer = FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestSimplelayoutView, self).setUp()
        self.setup_sample_ftis(self.layer['portal'])
        self.setup_block_views()
        self.container = create(Builder('sample container'))
        self.page_config = IPageConfiguration(self.container)
        self.url = self.container.absolute_url() + '/@@simplelayout-view'

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

    @browsing
    def test_render_blocks_not_in_page_configuration(self, browser):
        # Fallback for not saved blocks thru the simplelayout JS lib.
        create(Builder('sample block')
               .titled('TextBlock title')
               .within(self.container)
               .having(text=RichTextValue('The text'))
               )

        browser.login().visit(self.container, view='@@simplelayout-view')

        self.assertEqual(browser.url, self.url)
        self.assertEquals('OK',
                          browser.css('.sl-block').first.text)

    @browsing
    def test_invalid_simplelayout_save_state_request(self, browser):
        with self.assertRaises(BadRequest):
            browser.login().visit(self.container,
                                  view='sl-ajax-save-state-view',
                                  data={})

    @browsing
    def test_store_save_simplelayout_state_thru_view(self, browser):
        payload = {"data": json.dumps(self.payload)}
        browser.login().visit(self.container,
                              view='sl-ajax-save-state-view',
                              data=payload)

        self.assertEquals(self.payload, self.page_config.load())

    @browsing
    def test_render_blocks_in_different_layouts(self, browser):
        block1 = create(Builder('sample block')
                        .titled('Block 1')
                        .within(self.container))
        block2 = create(Builder('sample block')
                        .titled('Block 1')
                        .within(self.container))

        self.payload['default'][0]['cols'][0][
            'blocks'][0]['uid'] = IUUID(block1)
        self.payload['default'][1]['cols'][0][
            'blocks'][0]['uid'] = IUUID(block2)
        self.page_config.store(self.payload)
        transaction.commit()

        browser.login().visit(self.container)
        self.assertEquals(2,
                          len(browser.css('.sl-layout')),
                          'Expect 2 layouts')

        self.assertEquals(2,
                          len(browser.css('.sl-column.sl-col-1')),
                          'Expect two, one column layouts')

    @browsing
    def test_render_blocks_in_different_columns(self, browser):
        block1 = create(Builder('sample block')
                        .titled('Block 1')
                        .within(self.container))
        block2 = create(Builder('sample block')
                        .titled('Block 1')
                        .within(self.container))

        self.payload['default'][0]['cols'][0][
            'blocks'][0]['uid'] = IUUID(block1)
        self.payload['default'][1]['cols'][0][
            'blocks'][0]['uid'] = IUUID(block2)

        # Move Block into layout 1, column 2
        data_colmn = self.payload['default'][1]['cols'][0]
        self.payload['default'].pop()

        self.payload['default'][0]['cols'].append(data_colmn)
        self.page_config.store(self.payload)
        transaction.commit()

        browser.login().visit(self.container)
        self.assertEquals(2,
                          len(browser.css('.sl-column.sl-col-2')),
                          'Expect 2 columns')

    @browsing
    def test_skips_unavailable_blocks(self, browser):
        # The block may no longer exist or may not be visible for
        # the current user.

        block1 = create(Builder('sample block')
                        .titled('Block 1')
                        .within(self.container))

        self.payload['default'][0]['cols'][0][
            'blocks'][0]['uid'] = IUUID(block1)
        self.payload['default'][1]['cols'][0][
            'blocks'][0]['uid'] = '123xNONxEXISTINGxUIDx123'
        self.page_config.store(self.payload)
        transaction.commit()

        browser.login().visit(self.container)
        self.assertEquals(
            ['http://nohost/plone/samplecontainer/block-1'],
            map(lambda node: node.attrib.get('data-url'),
                browser.css('.sl-block')))

    @browsing
    def test_empty_block_state_does_not_break_the_view(self, browser):
        self.payload['default'][0]['cols'][0]['blocks'].append({})
        self.page_config.store(self.payload)
        transaction.commit()

        browser.login().visit(self.container)
        self.assertTrue(
            browser.css('body.template-simplelayout-view'),
            'Expect to be on the simplelayout template, not the error page.')

    @browsing
    def test_simplelayout_default_config_from_control_panel(self, browser):
        browser.login().visit(self.container, view='@@simplelayout-view')

        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISimplelayoutDefaultSettings)
        settings.slconfig = u'{"layouts": [1, 2]}'
        transaction.commit()

        browser.login().visit(self.container, view='@@simplelayout-view')
        data_attr_value = json.loads(browser.css(
            '[data-sl-settings]').first.attrib['data-sl-settings'])

        self.assertEquals([1, 2],
                          data_attr_value['layouts'],
                          'Expect the layout setting in default config.')

    @browsing
    def test_simplelayout_config_updated_by_permissions(self, browser):

        browser.login().visit(self.container, view='@@simplelayout-view')
        data_attr_value = json.loads(browser.css(
            '[data-sl-settings]').first.attrib['data-sl-settings'])

        self.assertTrue(data_attr_value['canChangeLayout'],
                        'Should have the Change layouts permission.')

        self.container.manage_permission('ftw.simplelayout: Change Layouts',
                                         roles=[],
                                         acquire=0)
        transaction.commit()

        browser.visit(self.container, view='@@simplelayout-view')
        data_attr_value = json.loads(browser.css(
            '[data-sl-settings]').first.attrib['data-sl-settings'])

        self.assertFalse(data_attr_value['canChangeLayout'],
                         'Should NOT have the Change layouts permission.')

    @browsing
    def test_prevent_layout_changes_if_not_allowed(self, browser):

        self.container.manage_permission('ftw.simplelayout: Change Layouts',
                                         roles=[],
                                         acquire=0)
        transaction.commit()

        with self.assertRaises(Unauthorized):
            self.payload['default'].append({'cols': [{}]})
            payload = {"data": json.dumps(self.payload)}
            browser.login().visit(self.container,
                                  view='sl-ajax-save-state-view',
                                  data=payload)

    @browsing
    def test_simplelayout_config_updated_by_adapter(self, browser):

        class ContainerConfigAdapter(object):
            implements(ISimplelayoutContainerConfig)

            def __init__(self, context, request):
                pass

            def __call__(self, settings):
                settings['layouts'] = [1]

            def default_page_layout(self):
                return None

        provideAdapter(ContainerConfigAdapter,
                       adapts=(ISampleSimplelayoutContainer, Interface))
        transaction.commit()

        try:
            browser.login().visit(self.container, view='@@simplelayout-view')
            data_attr_value = json.loads(browser.css(
                '[data-sl-settings]').first.attrib['data-sl-settings'])
            self.assertEquals([1], data_attr_value['layouts'])

        finally:
            # Unregister adapter - since the component registry is not isolatet
            # per test
            sm = getGlobalSiteManager()
            sm.unregisterAdapter(ContainerConfigAdapter,
                                 required=(
                                     ISampleSimplelayoutContainer, Interface),
                                 provided=ISimplelayoutContainerConfig)

    @browsing
    def test_simplelayout_default_page_layouts_by_adapter(self, browser):

        class ContainerConfigAdapter(object):
            implements(ISimplelayoutContainerConfig)

            def __init__(self, context, request):
                pass

            def __call__(self, settings):
                pass

            def default_page_layout(self):
                return {
                    "default": [
                        {"cols": [{"blocks": []},
                                  {"blocks": []}]}
                    ]
                }

        provideAdapter(ContainerConfigAdapter,
                       adapts=(ISampleSimplelayoutContainer, Interface))
        transaction.commit()

        try:
            browser.login().visit(self.container, view='@@simplelayout-view')
            # This should result in one layout with two columns
            self.assertEquals(1, len(browser.css('.sl-layout')))
            self.assertEquals(2, len(browser.css('.sl-column.sl-col-2')))

        finally:
            # Unregister adapter - since the component registry is not isolatet
            # per test
            sm = getGlobalSiteManager()
            sm.unregisterAdapter(ContainerConfigAdapter,
                                 required=(
                                     ISampleSimplelayoutContainer, Interface),
                                 provided=ISimplelayoutContainerConfig)

    @browsing
    def test_simplelayout_config_updated_view(self, browser):

        class CustomSimplelayoutView(SimplelayoutView):
            def update_simplelayout_settings(self, settings):
                settings['layouts'] = [1, 4]

        provideAdapter(CustomSimplelayoutView,
                       adapts=(Interface, Interface),
                       provides=IBrowserView,
                       name='customview')

        browser.login().visit(self.container, view='@@customview')
        data_attr_value = json.loads(browser.css(
            '[data-sl-settings]').first.attrib['data-sl-settings'])
        self.assertEquals([1, 4], data_attr_value['layouts'])

    @browsing
    def test_show_fallback_view_on_block_render_problems(self, browser):
        block = create(Builder('sample block')
                       .titled('TextBlock title')
                       .within(self.container))

        properties = getMultiAdapter((block, block.REQUEST),
                                     IBlockProperties)
        properties.set_view('block_view_broken')

        transaction.commit()

        browser.login().visit(self.container)
        self.assertEquals(
            'The block could not be rendered. Please check the log for '
            'details.',
            browser.css('.sl-block').first.text)

    @browsing
    def test_empty_sl_page_renders_at_least_one_layout(self, browser):
        browser.login().visit(self.container)

        # By default it's a one column layout.
        self.assertEquals(1,
                          len(browser.css('.sl-column.sl-col-1')),
                          'There should be at least a empty one column layout')

    @browsing
    def test_normalized_portal_type_as_css_klass_on_block(self, browser):
        create(Builder('sample block')
               .titled('TextBlock title')
               .within(self.container))
        browser.login().visit(self.container)
        self.assertEquals('sl-block sampleblock',
                          browser.css('.sl-block').first.attrib['class'],
                          'Expect "sample" as css klass on block structure.')

    @browsing
    def test_block_has_anchor(self, browser):
        create(Builder('sample block')
               .titled('Block 1')
               .within(self.container))

        browser.login().open(self.container)
        self.assertEqual(
            'block-1',
            browser.css('.sl-layout a').first.attrib['name']
        )

    @browsing
    def test_addable_block_types_view_property(self, browser):
        create(Builder('sample block')
               .titled('Block 1')
               .within(self.container))

        view = self.container.restrictedTraverse('@@simplelayout-view')
        self.assertEqual(
            ['SampleBlock'],
            view.addable_block_types()
        )

    @browsing
    def test_canEdit_is_false_if_border_disabled(self, browser):
        browser.login().visit(self.container, data={'disable_border': 1})
        data_attr_value = json.loads(browser.css(
            '[data-sl-settings]').first.attrib['data-sl-settings'])

        self.assertFalse(data_attr_value['canEdit'],
                         'Edit should be disabled if disable_border is there.')

    @browsing
    def test_sl_container_has_sl_edit_css_class(self, browser):
        browser.login().visit(self.container)
        self.assertTrue(len(browser.css('.sl-can-edit')),
                        'Expect the sl-can-edit class on sl-simplelayout.')

    @browsing
    def test_sl_container_no_sl_edi_css_class(self, browser):
        browser.login().visit(self.container, data={'disable_border': 1})
        self.assertFalse(len(browser.css('.sl-can-edit')),
                         'no sl-can-edit class expected.')
