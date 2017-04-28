from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING
from ftw.simplelayout.testing import SimplelayoutTestCase
from ftw.testbrowser import browsing
from plone import api
from plone.uuid.interfaces import IUUID
import json


class TestInnerEdit(SimplelayoutTestCase):

    layer = FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING

    def setUp(self):
        self.setup_sample_ftis(self.layer['portal'])
        self.setup_block_views()

        types_tool = api.portal.get_tool('portal_types')
        contentpage_fti = types_tool.get('SampleContainer')
        contentpage_fti.allowed_content_types = ('SampleFolderishBlock', )

        self.page = create(Builder('sample container'))
        self.folderishblock = create(Builder('sample folderish block'))

        self.innercontent = create(Builder('sample container')
                                   .within(self.folderishblock))

    def get_payload(self, content):
        uid = IUUID(content)
        return {'data': json.dumps({'uid': uid})}

        browser.visit(self.page,
                      view='sl-ajax-inner-edit-view',
                      data=self.get_payload(self.innercontent))

        self.assertEquals(
            '{0}/inner_edit.json'.format(self.innercontent.absolute_url()),
            browser.url)

    @browsing
    def test_edit_a_block_returns_json(self, browser):
        browser.login().visit(self.innercontent, view='inner_edit.json')

        self.assertEquals(json.loads(json.dumps(browser.contents)),
                          browser.contents)

    @browsing
    def test_edit_an_item_in_block_returns_content_and_proceed(self, browser):
        browser.login().visit(self.innercontent, view='inner_edit.json')
        response = json.loads(browser.contents)

        self.assertIn('content',
                      response,
                      'Response does not contain content.')

        self.assertIn('proceed',
                      response,
                      'Response does not contain proceed.')

    @browsing
    def test_inner_edit_content_contains_a_form(self, browser):
        browser.login().visit(self.innercontent, view='inner_edit.json')
        response = browser.json
        browser.parse(response['content'])

        self.assertTrue(browser.css('form'), 'No form found in content.')

    @browsing
    def test_inner_edit_proceed_is_false(self, browser):
        browser.login().visit(self.innercontent, view='inner_edit.json')
        response = browser.json

        self.assertFalse(response['proceed'], 'Proceed should be false.')

    @browsing
    def test_inner_edit_returns_the_block_content(self, browser):
        browser.login().visit(self.innercontent, view='inner_edit.json')
        response = browser.json

        browser.parse(response['content'])
        browser.fill({'Title': u'This is a title'})
        browser.find_button_by_label('Save').click()
        self.assertEquals({u'content': u'OK', u'proceed': True}, browser.json)

    @browsing
    def test_submit_inner_block_traverser_proceed_returns_true(self, browser):
        browser.login().visit(self.innercontent, view='inner_edit.json')
        response = browser.json

        browser.parse(response['content'])
        browser.fill({'Title': u'This is a title'})
        browser.find_button_by_label('Save').click()
        self.assertEquals({u'content': u'OK', u'proceed': True}, browser.json)
