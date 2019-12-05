from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.contenttypes.behaviors import ITeaser
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_CONTENT_TESTING
from ftw.testbrowser import browsing
from unittest import TestCase
from z3c.relationfield import RelationValue
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
import transaction


class TestTeaserBehavior(TestCase):

    layer = FTW_SIMPLELAYOUT_CONTENT_TESTING

    def setUp(self):
        self.page = create(Builder('sl content page'))
        self.intids = getUtility(IIntIds)

    def test_textblock_has_internal_link_and_external_link_field(self):
        textblock = create(Builder('sl textblock')
                           .within(self.page)
                           .having(external_link='http://www.4teamwork.ch')
                           .having(internal_link=RelationValue(
                                   self.intids.getId(self.page))))

        self.assertEquals('http://www.4teamwork.ch',
                          ITeaser(textblock).external_link)
        self.assertEquals(self.page,
                          ITeaser(textblock).internal_link.to_object)

    @browsing
    def test_broken_internal_link(self, browser):
        target = create(Builder('sl content page'))
        textblock = create(Builder('sl textblock')
                           .within(self.page)
                           .having(internal_link=RelationValue(
                                   self.intids.getId(target))))

        self.layer['portal'].manage_delObjects(ids=[target.getId()])
        transaction.commit()

        browser.login().visit(textblock, view='block_view')
        self.assertFalse(
            browser.css('a'),
            'Expect no link, since the internal target does not exist.')
