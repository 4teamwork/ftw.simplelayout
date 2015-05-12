from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING
from ftw.testbrowser import browsing
from plone.uuid.interfaces import IUUID
from unittest2 import TestCase
from zExceptions import BadRequest
import json


class TestEditBlock(TestCase):

    layer = FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING

    def setUp(self):
        self.page = create(Builder('sl content page'))
        self.block = create(Builder('sl textblock'))

    def get_payload(self, block):
        block = IUUID(block)
        return {'data': json.dumps({'block': block})}

    @browsing
    def test_redirector_redirects_to_edit_view(self, browser):
        browser.login()

        with self.assertRaises(BadRequest):
            browser.visit(self.page,
                          view='sl-ajax-edit-block-view',
                          data={})

            browser.visit(self.page,
                          view='sl-ajax-edit-block-view',
                          data={'data': json.dumps({'block': 'DUMMY'})})

        browser.visit(self.page,
                      view='sl-ajax-edit-block-view',
                      data=self.get_payload(self.block))

        self.assertEquals('{0}/edit'.format(self.block.absolute_url()),
                          browser.url)

    @browsing
    def test_edit_a_block_returns_json(self, browser):
        browser.login().visit(self.block, view='edit')

        self.assertEquals(json.loads(json.dumps(browser.contents)),
                          browser.contents)

    @browsing
    def test_edit_a_block_returns_content_and_proceed(self, browser):
        browser.login().visit(self.block, view='edit')
        response = json.loads(browser.contents)

        self.assertIn('content',
                      response,
                      'Response does not contain content.')

        self.assertIn('proceed',
                      response,
                      'Response does not contain proceed.')

    @browsing
    def test_edit_a_block_content_contains_a_form(self, browser):
        browser.login().visit(self.block, view='edit')
        response = browser.json
        browser.open_html(response['content'])

        self.assertTrue(browser.css('form'), 'No form found in content.')

    @browsing
    def test_edit_a_block_proceed_is_false(self, browser):
        browser.login().visit(self.block, view='edit')
        response = browser.json

        self.assertFalse(response['proceed'], 'Proceed should be false.')

    @browsing
    def test_edit_a_block_form_returns_block(self, browser):
        browser.login().visit(self.block, view='edit')
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
        browser.login().visit(self.block, view='edit')
        response = browser.json

        browser.open_html(response['content'])
        browser.fill({'Title': u'This is a TextBlock',
                      'Text': u'Some text'})
        browser.find_button_by_label('Save').click()

        response = browser.json
        browser.open_html(response['content'])
        self.assertTrue(
            response['proceed'], 'Proceed should be true after submitting the form.')
