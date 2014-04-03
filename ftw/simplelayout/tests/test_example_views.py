from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.slot import set_slot_information
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING
from ftw.testbrowser import browsing
from plone.app.textfield.value import RichTextValue
from unittest2 import TestCase
import transaction


class TestSimplelayoutTwoColumnsView(TestCase):

    layer = FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING

    @browsing
    def test_blocks_are_in_both_slots(self, browser):
        self.page = create(Builder('sl content page').titled(u'A page'))

        block_slot1 = create(Builder('sl textblock')
                             .titled(u'TextBlock Slot 1 title')
                             .within(self.page)
                             .having(text=RichTextValue('Text Slot 1'))
                             .having(show_title=True))
        set_slot_information(block_slot1, 'sl-slot-None')

        block_slot2 = create(Builder('sl textblock')
                             .titled(u'TextBlock Slot 2 title')
                             .within(self.page)
                             .having(text=RichTextValue('Text Slot 2'))
                             .having(show_title=True))
        set_slot_information(block_slot2, 'sl-slot-Slot2')
        transaction.commit()

        browser.login().visit(self.page, view='simplelayout_two_slots')

        self.assertEquals(
            'TextBlock Slot 1 title',
            browser.css('#sl-slot-None.simplelayout h2').first.text)

        self.assertIn('Text Slot 1',
                      browser.css('#sl-slot-None.simplelayout').first.text)

        self.assertEquals(
            'TextBlock Slot 2 title',
            browser.css('#sl-slot-Slot2.simplelayout h2').first.text)

        self.assertIn('Text Slot 2',
                      browser.css('#sl-slot-Slot2.simplelayout').first.text)


class TestSimplelayoutFourColumnsView(TestCase):

    layer = FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING

    def test_simplelayout_config(self):
        self.page = create(Builder('sl content page').titled(u'A page'))
        expect = ('{"columns": 4, '
                  '"images": 1, '
                  '"contentwidth": 960, '
                  '"margin_right": 10, '
                  '"contentarea": "#content", '
                  '"editable": true}')

        view = self.page.restrictedTraverse('@@simplelayout_four_columns')
        self.assertEquals(
            expect,
            view.load_default_settings(),
            'Wrong config.')
