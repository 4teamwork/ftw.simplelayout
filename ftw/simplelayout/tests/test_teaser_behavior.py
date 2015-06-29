from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_CONTENT_TESTING
from ftw.simplelayout.testing import IS_PLONE_5
from unittest2 import skipUnless
from unittest2 import TestCase
from z3c.relationfield import RelationValue
from zope.component import getUtility
from zope.intid.interfaces import IIntIds


if not IS_PLONE_5:
    from ftw.simplelayout.behaviors import ITeaser


@skipUnless(not IS_PLONE_5, 'requires plone < 5')
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
