from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING
from ftw.testbrowser import browsing
from plone.app.textfield.value import RichTextValue
from plone.app.uuid.utils import uuidToObject
from plone.namedfile.file import NamedBlobImage
from StringIO import StringIO
from unittest2 import TestCase
from z3c.relationfield import RelationValue
from zope.component import getUtility
from zope.intid.interfaces import IIntIds


class TestTextBlockRendering(TestCase):

    layer = FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING

    def setUp(self):
        self.page = create(Builder('sl content page'))

        self.image = StringIO(
            'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\x00\x00'
            '\x00!\xf9\x04\x04\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00'
            '\x01\x00\x00\x02\x02D\x01\x00;')

    @browsing
    def test_teaser_url_external(self, browser):
        block = create(Builder('sl textblock')
                       .within(self.page)
                       .titled('TextBlock title')
                       .having(text=RichTextValue('The text'))
                       .having(external_link='http://www.4teamwork.ch')
                       .having(image=NamedBlobImage(data=self.image.read(),
                                                    filename=u'test.gif')))

        browser.login().visit(block, view='@@block_view')
        self.assertEquals(
            'http://www.4teamwork.ch',
            browser.css('[data-simplelayout-url]').first.attrib['data-simplelayout-url'])

    @browsing
    def test_teaser_url_internal(self, browser):
        intids = getUtility(IIntIds)
        block = create(Builder('sl textblock')
                       .within(self.page)
                       .titled('TextBlock title')
                       .having(text=RichTextValue('The text'))
                       .having(internal_link=RelationValue(
                               intids.getId(self.page)))
                       .having(image=NamedBlobImage(data=self.image.read(),
                                                    filename=u'test.gif')))

        browser.login().visit(block, view='@@block_view')
        self.assertEquals(self.page.absolute_url(),
                          browser.css('[data-simplelayout-url]').first.attrib[
                              'data-simplelayout-url'])

    @browsing
    def test_sl_block_wrapper_contains_uid_data_attribute(self, browser):
        block = create(Builder('sl textblock')
                       .within(self.page)
                       .titled('TextBlock title')
                       .having(text=RichTextValue(u'The text with \xfc'))
                       .having(image=NamedBlobImage(data=self.image.read(),
                                                    filename=u'test.gif')))

        browser.login().visit(block, view='@@block_view')

        resolve_block = uuidToObject(
            browser.css('.sl-block-content').first.attrib['data-uid'])

        self.assertEquals(block, resolve_block)
