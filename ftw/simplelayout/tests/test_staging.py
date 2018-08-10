from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.configuration import synchronize_page_config_with_blocks
from ftw.simplelayout.interfaces import IBlockConfiguration
from ftw.simplelayout.interfaces import IPageConfiguration
from ftw.simplelayout.staging.interfaces import IBaseline
from ftw.simplelayout.staging.interfaces import IStaging
from ftw.simplelayout.staging.interfaces import IWorkingCopy
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_CONTENT_TESTING
from ftw.testing import staticuid
from plone.app.textfield.value import RichTextValue
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
            {'default': [{'cols': [{'blocks': [
                {'uid': 'baseline000000000000000000000002'},
                {'uid': 'baseline000000000000000000000003'}]}]}]},
            IPageConfiguration(baseline).load())

        with staticuid('workingcopy'):
            working_copy = IStaging(baseline).create_working_copy(self.portal)

        self.assertEquals(
            {'default': [{'cols': [{'blocks': [
                {'uid': 'workingcopy000000000000000000001'},
                {'uid': 'workingcopy000000000000000000002'}]}]}]},
            IPageConfiguration(working_copy).load())

    def test_apply_working_copy_copies_field_values_back_to_baseline(self):
        bl_page = create(Builder('sl content page')
                         .titled(u'original page title')
                         .with_blocks(Builder('sl textblock')
                                      .titled(u'original block title')
                                      .having(text=RichTextValue(
                                          u'<p>original block text</p>'))))

        wc_page = IStaging(bl_page).create_working_copy(self.portal)
        wc_page.setTitle(u'modified page title')
        wc_block = wc_page.objectValues()[0]
        wc_block.setTitle(u'modified block title')
        wc_block.text = RichTextValue(u'<p>modified block text</p>')

        IStaging(wc_page).apply_working_copy()
        bl_block = bl_page.objectValues()[0]
        self.assertEquals('modified page title', wc_page.Title())
        self.assertEquals('modified block title', bl_block.Title())
        self.assertEquals('<p>modified block text</p>', bl_block.text.output)

    def test_applying_removes_blocks_from_baseline_when_removed_in_working_copy(self):
        bl_page = create(Builder('sl content page').titled(u'Page')
                         .with_blocks(Builder('sl textblock').titled(u'Foo'))
                         .with_blocks(Builder('sl textblock').titled(u'Bar')))
        create(Builder('sl content page').titled(u'Subpage').within(bl_page))
        self.assertEquals(['foo', 'bar', 'subpage'], bl_page.objectIds())

        wc_page = IStaging(bl_page).create_working_copy(self.portal)
        self.assertEquals(['foo', 'bar'], wc_page.objectIds())
        wc_page.manage_delObjects(['foo'])
        self.assertEquals(['bar'], wc_page.objectIds())

        IStaging(wc_page).apply_working_copy()
        self.assertEquals(['bar', 'subpage'], bl_page.objectIds())

    def test_applying_adds_new_blocks(self):
        bl_page = create(Builder('sl content page').titled(u'Page'))
        self.assertEquals([], bl_page.objectIds())

        wc_page = IStaging(bl_page).create_working_copy(self.portal)
        create(Builder('sl textblock').titled(u'Foo').within(wc_page))
        IStaging(wc_page).apply_working_copy()

        self.assertEquals(['foo'], bl_page.objectIds())

    def test_applying_adds_new_containers_and_handles_recursion(self):
        bl_page = create(Builder('sl content page').titled(u'Page'))
        self.assertEquals([], bl_page.objectIds())

        wc_page = IStaging(bl_page).create_working_copy(self.portal)
        gallery = create(Builder('sl galleryblock').titled(u'Pictures').within(wc_page))
        create(Builder('image').titled('Sea').within(gallery))
        IStaging(wc_page).apply_working_copy()

        self.assertEquals(['pictures'], bl_page.objectIds())
        self.assertEquals(['sea'], bl_page.pictures.objectIds())

    def test_files_in_filelistingblocks_are_synced(self):
        bl_page = create(
            Builder('sl content page').titled(u'Page')
            .with_blocks(Builder('sl listingblock').titled(u'Downloads')
                         .with_files(Builder('file').titled(u'One'),
                                     Builder('file').titled(u'Two'))))

        wc_page = IStaging(bl_page).create_working_copy(self.portal)
        wc_page.downloads.one.setTitle('The first one')
        create(Builder('file').titled(u'Three').within(wc_page.downloads))
        wc_page.downloads.manage_delObjects(['two'])
        IStaging(wc_page).apply_working_copy()

        self.assertEquals('The first one', bl_page.downloads.one.Title())
        self.assertEquals(['one', 'three'], bl_page.downloads.objectIds())

    def test_sl_page_state_is_updated_when_applying_working_copy(self):
        with staticuid('baseline'):
            baseline = create(Builder('sl content page').titled(u'A page')
                              .with_blocks(Builder('sl textblock').titled(u'First')))

        self.assertEquals(
            {'default': [{'cols': [{'blocks': [
                {'uid': 'baseline000000000000000000000002'}]}]}]},
            IPageConfiguration(baseline).load())

        with staticuid('workingcopy'):
            working_copy = IStaging(baseline).create_working_copy(self.portal)

        self.assertEquals(
            {'default': [{'cols': [{'blocks': [
                {'uid': 'workingcopy000000000000000000001'}]}]}]},
            IPageConfiguration(working_copy).load())

        with staticuid('editing'):
            create(Builder('sl textblock').titled(u'Second').within(working_copy))
            synchronize_page_config_with_blocks(working_copy)

        self.assertEquals(
            {'default': [{'cols': [{'blocks': [
                {'uid': 'workingcopy000000000000000000001'},
                {'uid': 'editing0000000000000000000000001'}]}]}]},
            IPageConfiguration(working_copy).load())

        with staticuid('applying'):
            IStaging(working_copy).apply_working_copy()

        self.assertEquals(
            {'default': [{'cols': [{'blocks': [
                {'uid': 'baseline000000000000000000000002'},
                {'uid': 'editing0000000000000000000000001'}]}]}]},
            IPageConfiguration(baseline).load())

    def test_sl_block_state_is_copied_when_applying(self):
        baseline = create(Builder('sl content page').titled(u'A page')
                          .with_blocks(Builder('sl textblock').titled(u'Block')))
        self.assertEqual({}, IBlockConfiguration(baseline.block).load())

        working_copy = IStaging(baseline).create_working_copy(self.portal)
        self.assertEqual({}, IBlockConfiguration(working_copy.block).load())

        IBlockConfiguration(working_copy.block).store({'scale': 'mini'})
        self.assertEqual({}, IBlockConfiguration(baseline.block).load())
        self.assertEqual({'scale': 'mini'}, IBlockConfiguration(working_copy.block).load())

        IStaging(working_copy).apply_working_copy()
        self.assertEqual({'scale': 'mini'}, IBlockConfiguration(baseline.block).load())

    def test_working_copy_is_removed_after_applying(self):
        bl_page = create(Builder('sl content page').titled(u'A page'))
        wc_page = IStaging(bl_page).create_working_copy(self.portal)
        self.assertIn(wc_page.getId(), self.portal.objectIds())
        IStaging(wc_page).apply_working_copy()
        self.assertNotIn(wc_page.getId(), self.portal.objectIds())

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