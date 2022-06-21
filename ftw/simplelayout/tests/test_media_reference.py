from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_CONTENT_TESTING
from ftw.testbrowser import browsing
from plone.app.testing import TEST_USER_ID
from unittest import TestCase
from z3c.relationfield import RelationValue
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
import transaction


class TestMediaReference(TestCase):

    layer = FTW_SIMPLELAYOUT_CONTENT_TESTING

    def setUp(self):
        super(TestMediaReference, self).setUp()
        self.portal = self.layer['portal']
        self.page = create(Builder('sl content page').titled(u'A page'))
        self.intids = getUtility(IIntIds)

    @browsing
    def test_listing_shows_link_to_create_content(self, browser):
        create(Builder('sl listingblock')
               .titled('My listingblock')
               .having(show_title=True)
               .within(self.page))

        browser.login().visit(self.page)
        self.assertTrue(browser.css('.edit-hints button'), 'Expect a button to add the media folder')

    @browsing
    def test_create_and_link_mediafolder(self, browser):
        listingblock = create(Builder('sl listingblock')
                              .titled('My listingblock')
                              .having(show_title=True)
                              .within(self.page))

        browser.login().visit(self.page)
        browser.css('.edit-hints button').first.click()

        self.assertEquals(listingblock.mediafolder.to_object,
                          self.page.objectValues()[1])

    @browsing
    def test_show_content_from_media_folder(self, browser):
        mediafolder = create(Builder('mediafolder')
                             .titled(u'media folder')
                             .within(self.page))

        file_ = create(Builder('file')
                       .titled('Test file')
                       .having(creators=(TEST_USER_ID.decode('utf-8'), ))
                       .with_dummy_content()
                       .within(mediafolder))

        listingblock = create(Builder('sl listingblock')
                              .titled('My listingblock')
                              .having(show_title=True)
                              .within(self.page))
        listingblock.mediafolder = RelationValue(self.intids.getId(mediafolder))
        transaction.commit()

        browser.login().visit(self.page)

        modified = file_.modified().strftime('%d.%m.%Y')
        browser.login().visit(self.page)
        self.assertEquals([['Type', 'Title', 'modified'],
                           ['', 'Test file', modified]],
                          browser.css('.sl-block table').first.lists())
