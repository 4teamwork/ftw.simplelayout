from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.interfaces import ISimplelayoutDefaultSettings
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_CONTENT_TESTING
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.dexterity import erroneous_fields
from plone import api
from unittest import TestCase
import transaction


class TestImageLimitValidation(TestCase):

    layer = FTW_SIMPLELAYOUT_CONTENT_TESTING

    def set_config(self, config=[]):
        api.portal.set_registry_record(
            'image_limits', config, ISimplelayoutDefaultSettings)

        transaction.commit()

    @browsing
    def test_raise_invalid_if_hard_limit_is_not_satisfied_for_width(self, browser):
        page = create(Builder('sl content page'))
        block = create(Builder('sl textblock').within(page).with_dummy_image())

        self.set_config({
            block.portal_type: [
                u'hard: width={}'.format(block.image._width + 100)
            ]}
        )

        browser.login().visit(block, view="edit")
        browser.find_button_by_label('Save').click()

        self.assertEqual(
            [["The image doesn't fit the required dimensions of width: 2020px (current: 1920px)"]],
            erroneous_fields().values())

    @browsing
    def test_raise_invalid_if_hard_limit_is_not_satisfied_for_height(self, browser):
        page = create(Builder('sl content page'))
        block = create(Builder('sl textblock').within(page).with_dummy_image())

        self.set_config({
            block.portal_type: [
                u'hard: height={}'.format(block.image._height + 100)
            ]}
        )

        browser.login().visit(block, view="edit")
        browser.find_button_by_label('Save').click()

        self.assertEqual(
            [["The image doesn't fit the required dimensions of height: 1180px (current: 1080px)"]],
            erroneous_fields().values())

    @browsing
    def test_raise_invalid_if_hard_limit_is_not_satisfied_for_width_and_height(self, browser):
        page = create(Builder('sl content page'))
        block = create(Builder('sl textblock').within(page).with_dummy_image())

        self.set_config({
            block.portal_type: [
                u'hard: width={}, height={}'.format(
                    block.image._width + 100,
                    block.image._height + 100)
            ]}
        )

        browser.login().visit(block, view="edit")
        browser.find_button_by_label('Save').click()

        self.assertEqual(
            [["The image doesn't fit the required dimensions of "
              "width: 2020px (current: 1920px) and height: 1180px (current: 1080px)"]],
            erroneous_fields().values())
