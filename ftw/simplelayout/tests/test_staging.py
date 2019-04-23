from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.configuration import synchronize_page_config_with_blocks
from ftw.simplelayout.contenttypes.contents.interfaces import IContentPage
from ftw.simplelayout.interfaces import IBlockConfiguration
from ftw.simplelayout.interfaces import IPageConfiguration
from ftw.simplelayout.staging.interfaces import IBaseline
from ftw.simplelayout.staging.interfaces import IStaging
from ftw.simplelayout.staging.interfaces import IWorkingCopy
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_CONTENT_TESTING
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from ftw.testing import freeze
from ftw.testing import staticuid
from plone.app.textfield.value import RichTextValue
from plone.uuid.interfaces import IUUID
from unittest2 import TestCase
from zope.component import adapter
from zope.interface.verify import verifyObject
from zope.lifecycleevent.interfaces import IObjectAddedEvent
import transaction


@adapter(IContentPage, IObjectAddedEvent)
def create_block_when_page_is_added(parent, event):
    create(Builder('sl textblock').titled(u'Auto generated').within(parent))


class TestWorkingCopy(TestCase):
    layer = FTW_SIMPLELAYOUT_CONTENT_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

        for fti in (self.portal.portal_types.File,
                    self.portal.portal_types.Image):
            if not hasattr(fti, 'behaviors'):
                # File and image are not DX in Plone 4.3.x, but AT.
                continue
            behaviors = list(fti.behaviors)
            behaviors.remove('plone.app.dexterity.behaviors.filename.INameFromFileName')
            behaviors += ['plone.app.content.interfaces.INameFromTitle']
            fti.behaviors = tuple(behaviors)

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
        self.assertEquals(2, baseline.objectCount())

        working_copy = IStaging(baseline).create_working_copy(self.portal)
        self.assertEquals({'textblock'}, set(working_copy.objectIds()))
        self.assertEquals(1, working_copy.objectCount())
        self.assertEquals({'child-page', 'textblock'}, set(baseline.objectIds()))
        self.assertEquals(2, baseline.objectCount())
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
                {'uid': 'applying000000000000000000000001'}]}]}]},
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

    def test_html_references_within_page_are_rewritten(self):
        self.maxDiff = None
        bl_page = create(Builder('sl content page').titled(u'A page'))
        with staticuid('baseline'):
            bl_one = create(Builder('sl textblock').titled(u'One').within(bl_page))
            self.assertEquals('baseline000000000000000000000001', IUUID(bl_one))
            bl_two = create(Builder('sl textblock').titled(u'Two').within(bl_page))
            self.assertEquals('baseline000000000000000000000002', IUUID(bl_two))
            create(Builder('sl textblock').titled(u'ToC').within(bl_page)
                   .having(text=RichTextValue(u'''
<p>
  <a class="internal-link" href="resolveuid/baseline000000000000000000000001">One</a>
</p>
                            '''.strip())))

        with staticuid('workingcopy'):
            wc_page = IStaging(bl_page).create_working_copy(self.portal)
            self.assertEquals('workingcopy000000000000000000001', IUUID(wc_page['one']))
            self.assertEquals('workingcopy000000000000000000002', IUUID(wc_page['two']))

        self.assertMultiLineEqual(u'''
<p>
  <a class="internal-link" href="resolveuid/workingcopy000000000000000000001">One</a>
</p>
        '''.strip(), wc_page.toc.text.raw.strip())

        with staticuid('editing'):
            wc_three = create(Builder('sl textblock').titled(u'Three').within(wc_page))
            self.assertEquals('editing0000000000000000000000001', IUUID(wc_three))

        wc_page.toc.text = RichTextValue(u'''
<p>
  <a class="internal-link" href="resolveuid/workingcopy000000000000000000001">One</a>
  <a class="internal-link" href="resolveuid/workingcopy000000000000000000002">Two</a>
  <a class="internal-link" href="resolveuid/editing0000000000000000000000001">Three</a>
</p>
        '''.strip())

        with staticuid('apply'):
            IStaging(wc_page).apply_working_copy()

        self.assertMultiLineEqual(u'''
<p>
  <a class="internal-link" href="resolveuid/baseline000000000000000000000001">One</a>
  <a class="internal-link" href="resolveuid/baseline000000000000000000000002">Two</a>
  <a class="internal-link" href="resolveuid/apply000000000000000000000000001">Three</a>
</p>
        '''.strip(), bl_page.toc.text.raw.strip())

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

    @browsing
    def test_message_is_displayed_on_working_copy(self, browser):
        baseline = create(Builder('sl content page').titled(u'A page'))
        with freeze(datetime(2017, 7, 24)):
            working_copy = IStaging(baseline).create_working_copy(self.portal)

        transaction.commit()

        browser.login().open(working_copy)
        statusmessages.assert_message(
            'This is the working copy of test_user_1_, created at Jul 24, 2017.')

    @browsing
    def test_message_is_displayed_on_baseline(self, browser):
        baseline = create(Builder('sl content page').titled(u'A page'))
        with freeze(datetime(2017, 7, 24)):
            IStaging(baseline).create_working_copy(self.portal)

        transaction.commit()

        browser.login().open(baseline)
        statusmessages.assert_message(
            'test_user_1_ is working on this page in a http://nohost/plone/copy_of_a-page copy created at Jul 24, 2017.')

    @browsing
    def test_does_not_break_with_reference_to_sub_page(self, browser):
        """When pasting an object, the linkintegrity checker verifies the references.
        When creating the working copy, the tree is filtered while copy/pasting the
        page.
        Regression: when a block of the baseline contains a link to a sub page, the link
        integrity checker failed since it was executed while the tree still was filtered
        and thus the sub page was not reachable with traversal at all.
        """
        baseline = create(Builder('sl content page').titled(u'Baseline'))

        with staticuid('childpage'):
            create(Builder('sl content page').titled(u'Childpage')
                   .within(baseline))

        create(Builder('sl textblock').titled(u'Block').within(baseline)
               .having(text=RichTextValue(u'''
               <p>
                   <a class="internal-link"
                      href="resolveuid/childpage00000000000000000000001">Childpage</a>
               </p>'''.strip())))

        IStaging(baseline).create_working_copy(self.portal)

    @browsing
    def test_no_children_added_when_cloning(self, browser):
        """Some FTIs have subscribors which add children when an object is created.
        Example: when a news folder (ftw.news) is created, a news listing block is added.

        But when creating a working copy of such an object, we probably already have this
        kind of block and do not want to create an additional one in the clone step.

        Therefore all children created in the cloning step must be removed.
        """
        self.portal.getSiteManager().registerHandler(create_block_when_page_is_added)

        baseline = create(Builder('sl content page').titled(u'Baseline'))
        self.assertEquals(['auto-generated'], baseline.objectIds())

        working_copy = IStaging(baseline).create_working_copy(self.portal)
        self.assertEquals(['auto-generated'], working_copy.objectIds())

    def assert_staging_interfaces(self, expected, obj):
        expected = set(expected)
        got = set(filter(lambda iface: iface.providedBy(obj), (IBaseline, IWorkingCopy)))
        self.assertEquals(expected, got, 'Provided interfaces unexpected for {!r}'.format(obj))
