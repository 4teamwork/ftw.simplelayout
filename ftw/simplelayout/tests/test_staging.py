from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.interfaces import IPageConfiguration
from ftw.simplelayout.staging.interfaces import IBaseline
from ftw.simplelayout.staging.interfaces import IStaging
from ftw.simplelayout.staging.interfaces import IWorkingCopy
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_CONTENT_TESTING
from ftw.testing import staticuid
from plone.uuid.interfaces import IUUID
from unittest2 import TestCase
from zope.interface.verify import verifyObject


class TestWorkingCopy(TestCase):
    layer = FTW_SIMPLELAYOUT_CONTENT_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_staging_manager_implements_interface(self):
        page = create(Builder('sl content page'))
        verifyObject(IStaging, IStaging(page))

    def test_is_baseline(self):
        baseline = create(Builder('sl content page').titled(u'A page'))
        self.assertFalse(IStaging(baseline).is_baseline())
        working_copy = IStaging(baseline).create_working_copy(self.portal)
        self.assertTrue(IStaging(baseline).is_baseline())
        self.assertFalse(IStaging(working_copy).is_baseline())

    def test_is_working_copy(self):
        baseline = create(Builder('sl content page').titled(u'A page'))
        self.assertFalse(IStaging(baseline).is_working_copy())
        working_copy = IStaging(baseline).create_working_copy(self.portal)
        self.assertFalse(IStaging(baseline).is_working_copy())
        self.assertTrue(IStaging(working_copy).is_working_copy())

    def test_get_baseline(self):
        baseline = create(Builder('sl content page').titled(u'A page'))
        self.assertIsNone(IStaging(baseline).get_baseline())
        working_copy = IStaging(baseline).create_working_copy(self.portal)
        self.assertIsNone(IStaging(baseline).get_baseline())
        self.assertEquals(baseline, IStaging(working_copy).get_baseline())

    def test_get_working_copies(self):
        baseline = create(Builder('sl content page').titled(u'A page'))
        self.assertIsNone(IStaging(baseline).get_working_copies())
        working_copy = IStaging(baseline).create_working_copy(self.portal)
        self.assertEquals([working_copy], IStaging(baseline).get_working_copies())
        self.assertIsNone(IStaging(working_copy).get_working_copies())

    def test_create_working_copy_of_page(self):
        baseline = create(Builder('sl content page').titled(u'A page'))
        self.assert_staging_interfaces((), baseline)
        working_copy = IStaging(baseline).create_working_copy(self.portal)
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

    def test_UIDS_in_sl_state_are_updated_when_creating_working_copy(self):
        with staticuid('baseline'):
            baseline = create(Builder('sl content page').titled(u'A page')
                              .with_blocks(Builder('sl textblock').titled(u'First'),
                                           Builder('sl textblock').titled(u'Second')))

        self.assertEquals(
            {'default': [{'cols': [{'blocks': [{'uid': 'baseline000000000000000000000002'},
                                               {'uid': 'baseline000000000000000000000003'}]}]}]},
            IPageConfiguration(baseline).load())

        with staticuid('workingcopy'):
            working_copy = IStaging(baseline).create_working_copy(self.portal)

        self.assertEquals(
            {'default': [{'cols': [{'blocks': [{'uid': 'workingcopy000000000000000000001'},
                                               {'uid': 'workingcopy000000000000000000002'}]}]}]},
            IPageConfiguration(working_copy).load())

    def test_discard_working_copy(self):
        baseline = create(Builder('sl content page').titled(u'A page'))
        self.assertFalse(IStaging(baseline).is_baseline())
        self.assertIsNone(IStaging(baseline).get_working_copies())
        self.assertFalse(IStaging(baseline).is_working_copy())
        self.assertIsNone(IStaging(baseline).get_baseline())

        working_copy = IStaging(baseline).create_working_copy(self.portal)
        self.assertTrue(IStaging(baseline).is_baseline())
        self.assertEquals([working_copy], IStaging(baseline).get_working_copies())
        self.assertTrue(IStaging(working_copy).is_working_copy())
        self.assertEquals(baseline, IStaging(working_copy).get_baseline())

        IStaging(working_copy).discard_working_copy()
        self.assertNotIn(working_copy.getId(), self.portal.objectIds())
        self.assertFalse(IStaging(baseline).is_baseline())
        self.assertIsNone(IStaging(baseline).get_working_copies())
        self.assertFalse(IStaging(baseline).is_working_copy())
        self.assertIsNone(IStaging(baseline).get_baseline())

    def assert_staging_interfaces(self, expected, obj):
        expected = set(expected)
        got = set(filter(lambda iface: iface.providedBy(obj), (IBaseline, IWorkingCopy)))
        self.assertEquals(expected, got, 'Provided interfaces unexpected for {!r}'.format(obj))
