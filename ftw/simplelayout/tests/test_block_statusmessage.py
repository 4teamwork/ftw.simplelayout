from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING
from ftw.simplelayout.testing import SimplelayoutTestCase
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages


class TestBlockStatusmessage(SimplelayoutTestCase):

    layer = FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING

    def setUp(self):
        self.setup_sample_ftis(self.layer['portal'])
        self.setup_block_views()
        self.page = create(Builder('sample container'))

    @browsing
    def test_NO_statusmessage_on_block_creation(self, browser):
        browser.login().visit(self.page, view="++add_block++SampleBlock")
        response = browser.json

        browser.parse(response['content'])
        browser.fill({'Title': u'This is a TextBlock',
                      'Text': u'Some text'})
        browser.find_button_by_label('Save').click()

        browser.visit(self.page)
        statusmessages.assert_no_messages()

    @browsing
    def test_NO_statusmessage_on_block_modification(self, browser):
        block = create(Builder('sample block'))
        browser.login().visit(block, view='edit.json')
        response = browser.json

        browser.parse(response['content'])
        browser.fill({'Title': u'This is a TextBlock',
                      'Text': u'Some text'})
        browser.find_button_by_label('Save').click()

        browser.visit(self.page)
        statusmessages.assert_no_messages()
