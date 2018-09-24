from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.images.limits.limits import ImageLimits
from ftw.simplelayout.interfaces import ISimplelayoutDefaultSettings
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_CONTENT_TESTING
from ftw.simplelayout.testing import SimplelayoutTestCase
from ftw.testbrowser import browsing
from ftw.testbrowser.tests.helpers import asset
from plone import api
import transaction


class TestCropping(SimplelayoutTestCase):

    layer = FTW_SIMPLELAYOUT_CONTENT_TESTING

    def image_limits(self, config, context=None):
        limits = ImageLimits(context)
        limits.limit_configuration = config

        return limits

    @browsing
    def test_cropping_view_returns_json(self, browser):
        page = create(Builder('sl content page'))
        block = create(Builder('sl textblock').within(page).with_dummy_image())

        browser.login().visit(block, view='image_cropping.json')

        self.assertIsInstance(browser.json, dict)

    @browsing
    def test_default_buttons(self, browser):
        page = create(Builder('sl content page'))
        block = create(Builder('sl textblock').within(page).with_dummy_image())

        browser.login().visit(block, view='image_cropping.json')
        browser.open_html(browser.json.get('content'))

        self.assertTrue(browser.css('.btnDragModeMove'))
        self.assertTrue(browser.css('.btnDragModeCrop'))

        self.assertTrue(browser.css('.btnZoomIn'))
        self.assertTrue(browser.css('.btnZoomOut'))

        self.assertEqual(
            ['4:3', '16:9'],
            [el.text for el in browser.css('.btnAspectRatioButton')]
            )

        self.assertTrue(browser.css('.btnClear'))

    @browsing
    def test_ratio_buttons_are_generated_from_registry(self, browser):
        page = create(Builder('sl content page'))
        block = create(Builder('sl textblock').within(page).with_dummy_image())

        self._set_settings({
            block.portal_type: [u'free => 0']
        })

        browser.login().visit(block, view='image_cropping.json')
        browser.open_html(browser.json.get('content'))

        self.assertEqual(
            ['free'],
            [el.text for el in browser.css('.btnAspectRatioButton')]
            )

        self.assertEqual(
            ['0'],
            [el.get('data-value') for el in browser.css('.btnAspectRatioButton')]
            )

    @browsing
    def test_remove_cropped_image_if_main_image_has_changed(self, browser):
        page = create(Builder('sl content page'))
        block = create(Builder('sl textblock').within(page)
                       .with_cropped_image())

        self.assertIsNotNone(block.cropped_image)

        browser.login().visit(block, view='edit.json')
        browser.parse(browser.json['content'])

        with asset('mario.gif') as mario:
            browser.fill({'Image': (mario.read(), 'mario.gif')}).save()

        self.assertIsNone(block.cropped_image)

    def _set_settings(self, setting):
        api.portal.set_registry_record(
            name='image_cropping_aspect_ratios',
            value=setting,
            interface=ISimplelayoutDefaultSettings)

        transaction.commit()
