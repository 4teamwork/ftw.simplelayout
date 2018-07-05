from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.staging.interfaces import IBaseline
from ftw.simplelayout.staging.interfaces import IStaging
from ftw.simplelayout.staging.interfaces import IWorkingCopy
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_CONTENT_TESTING
from plone.uuid.interfaces import IUUID
from unittest2 import TestCase
from zope.interface.verify import verifyObject
import transaction


class TestWorkingCopy(TestCase):
    layer = FTW_SIMPLELAYOUT_CONTENT_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_staging_manager_implements_interface(self):
        page = create(Builder('sl content page'))
        verifyObject(IStaging, IStaging(page))

    def test_create_working_copy_of_page(self):
        baseline = create(Builder('sl content page').titled(u'A page'))
        self.assert_staging_interfaces((), baseline)
        working_copy = IStaging(baseline).create_working_copy(self.portal)
        transaction.commit()

        self.assertTrue(baseline._p_oid)
        self.assertTrue(working_copy._p_oid)
        self.assertNotEquals(baseline._p_oid, working_copy._p_oid)
        self.assertNotEquals(IUUID(baseline), IUUID(working_copy))
        self.assertEquals(baseline.Title(), working_copy.Title())
        self.assert_staging_interfaces({IBaseline}, baseline)
        self.assert_staging_interfaces({IWorkingCopy}, working_copy)

    def test_working_copy_contains_blocks_but_not_child_pages(self):
        baseline = create(Builder('sl content page').titled(u'A page'))
        create(Builder('sl content page').titled(u'Child page').within(baseline))
        create(Builder('sl textblock').titled(u'Textblock').within(baseline))
        self.assertEquals({'child-page', 'textblock'}, set(baseline.objectIds()))

        working_copy = IStaging(baseline).create_working_copy(self.portal)
        self.assertEquals({'textblock'}, set(working_copy.objectIds()))
        self.assertEquals({'child-page', 'textblock'}, set(baseline.objectIds()))
        self.assertNotEquals(IUUID(baseline['textblock']), IUUID(working_copy['textblock']))

    def assert_staging_interfaces(self, expected, obj):
        expected = set(expected)
        got = set(filter(lambda iface: iface.providedBy(obj), (IBaseline, IWorkingCopy)))
        self.assertEquals(expected, got, 'Provided interfaces unexpected for {!r}'.format(obj))
