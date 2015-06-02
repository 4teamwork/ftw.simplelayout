from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING
from ftw.testbrowser import browsing
from unittest2 import TestCase
import json


class TestAddBlock(TestCase):

    layer = FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING

    def setUp(self):
        self.page = create(Builder('sl content page'))
        self.textblockaddtraverser = '++add_block++ftw.simplelayout.TextBlock'

    @browsing
    def test_add_block_traverser_returns_json(self, browser):
        browser.login().visit(self.page, view=self.textblockaddtraverser)

        self.assertEquals(json.loads(json.dumps(browser.contents)),
                          browser.contents)

    @browsing
    def test_add_block_traverser_returns_content_and_proceed(self, browser):
        browser.login().visit(self.page, view=self.textblockaddtraverser)
        response = json.loads(browser.contents)

        self.assertIn('content',
                      response,
                      'Response does not contain content.')

        self.assertIn('proceed',
                      response,
                      'Response does not contain proceed.')

    @browsing
    def test_add_block_traverser_content_contains_a_form(self, browser):
        browser.login().visit(self.page, view=self.textblockaddtraverser)
        response = browser.json
        browser.open_html(response['content'])

        self.assertTrue(browser.css('form'), 'No form found in content.')

    @browsing
    def test_add_block_traverser_proceed_is_false(self, browser):
        browser.login().visit(self.page, view=self.textblockaddtraverser)
        response = browser.json

        self.assertFalse(response['proceed'], 'Proceed should be false.')

    @browsing
    def test_submit_add_block_traverser_form_returns_block(self, browser):
        browser.login().visit(self.page, view=self.textblockaddtraverser)
        response = browser.json

        browser.open_html(response['content'])
        browser.fill({'Title': u'This is a TextBlock',
                      'Text': u'Some text'})
        browser.find_button_by_label('Save').click()

        response = browser.json
        browser.open_html(response['content'])
        self.assertFalse(browser.css('form'), 'No form expected.')
        self.assertEquals('This is a TextBlock',
                          browser.css('h2').first.text)

    @browsing
    def test_submit_add_block_traverser_proceed_returns_true(self, browser):
        browser.login().visit(self.page, view=self.textblockaddtraverser)
        response = browser.json

        browser.open_html(response['content'])
        browser.fill({'Title': u'This is a TextBlock',
                      'Text': u'Some text'})
        browser.find_button_by_label('Save').click()

        response = browser.json
        browser.open_html(response['content'])
        self.assertTrue(
            response['proceed'], 'Proceed should be true after submitting the form.')
