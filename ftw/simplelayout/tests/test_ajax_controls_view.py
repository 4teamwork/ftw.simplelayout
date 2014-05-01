from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING
from ftw.testbrowser import browsing
from plone.app.textfield.value import RichTextValue
from plone.uuid.interfaces import IUUID
from unittest2 import TestCase
from zExceptions import BadRequest
from zope.component import getMultiAdapter


class TestAjaxReloadView(TestCase):

    layer = FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING

    def setUp(self):
        self.page = create(Builder('sl content page'))
        self.block = create(Builder('sl textblock')
                            .within(self.page)
                            .having(text=RichTextValue('The text')))

    @browsing
    def test_edit_and_delete(self, browser):

        browser.login().visit(self.block,
                              view='sl-ajax-block-controls',
                              data={'uuid': IUUID(self.block)})

        self.assertTrue(browser.css('.sl-edit'))
        self.assertTrue(browser.css('.sl-delete'))

    @browsing
    def test_no_uuid(self, browser):
        with self.assertRaises(BadRequest):
            browser.login().visit(self.block,
                                  view='sl-ajax-block-controls')

    @browsing
    def test_unknown_uuid(self, browser):
        with self.assertRaises(BadRequest):
            browser.login().visit(self.block,
                                  view='sl-ajax-block-controls',
                                  data={'uuid': 'dummy-uid'})

    def test_get_block_views(self):
        self.block.REQUEST.set('uuid', IUUID(self.block))
        controlsview = getMultiAdapter((self.block, self.block.REQUEST),
                                       name='sl-ajax-block-controls')

        controlsview()
        self.assertIsNone(controlsview.views())
