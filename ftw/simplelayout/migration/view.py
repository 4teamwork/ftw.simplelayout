from ftw.simplelayout.behaviors import ITeaser
from plone.app.contenttypes.migration import migration
from plone.app.contenttypes.migration.browser import pass_fn
from plone.app.contenttypes.migration.browser import PATCH_NOTIFY
from plone.app.contenttypes.migration.patches import patched_insertForwardIndexEntry
from plone.app.uuid.utils import uuidToObject
from Products.CMFCore.utils import getToolByName
from Products.contentmigration.utils import patch
from Products.contentmigration.utils import undoPatch
from Products.Five.browser import BrowserView
from Products.PluginIndexes.UUIDIndex.UUIDIndex import UUIDIndex
from simplelayout.base.interfaces import ISimpleLayoutBlock
from simplelayout.base.interfaces import ISlotA
from simplelayout.base.interfaces import ISlotB
from simplelayout.base.interfaces import ISlotC
from simplelayout.base.interfaces import ISlotD
from z3c.relationfield import RelationValue
from zope.component import getUtility
from zope.intid.interfaces import IIntIds


def restore_teaser_reference(portal):
    catalog = getToolByName(portal, "portal_catalog")
    for brain in catalog(portal_type='ftw.simplelayout.TextBlock'):
        obj = brain.getObject()
        if hasattr(obj, '_teaser_reference_uid'):
            intids = getUtility(IIntIds)
            reference = uuidToObject(obj._teaser_reference_uid)
            intid = intids.getId(reference)
            ITeaser(obj).internal_link = RelationValue(intid)


class Migration(BrowserView):
    """Migration view for ftw.contentpage to ftw.simplelayout.
    This view uses the concept and some methods of the plone.app.contenttypes
    migration view."""

    # template = ViewPageTemplateFile('migration_view.pt')

    def __init__(self, context, request):
        super(Migration, self).__init__(context, request)
        self.portal = None
        self.catalog = None
        self.link_integrity_state = False
        self.stats = {}

    def __call__(self):
        self.portal = self.context
        self.catalog = self.portal.portal_catalog

        self.link_integrity_check(enable=False)
        # Switch of setModificationDate on changes
        self.patch_notify_modified()
        # patch UUIDIndex - Prevent UUID Error-Messages when migrating folders.
        patch(
            UUIDIndex,
            'insertForwardIndexEntry',
            patched_insertForwardIndexEntry)

        # This prevents firing several unwanted events, like blockMoved, which
        # removes the slot interface (SlotA, SlotB, etc.) while migrating all
        # children of a ContentPage.
        self.store_block_marker_interface()

        # Migration
        self.migrate_contentpage()
        self.migrate_textblock()
        self.migrate_imageblock()

        self.catalog.clearFindAndRebuild()

        # restore references (only relatedItems) and cleanup
        migration.restoreReferences(self.portal,
                                    True,
                                    ['ftw.simplelayout.ContentPage',
                                     'ftw.simplelayout.TextBlock'])

        restore_teaser_reference(self.portal)

        self.link_integrity_check(enable=True)
        self.reset_notify_modified()
        # unpatch UUIDIndex
        undoPatch(UUIDIndex, 'insertForwardIndexEntry')

        return self.stats

    def migrate_contentpage(self):
        from ftw.contentpage.interfaces import IContentPage
        from ftw.simplelayout.migration.contentpage_migration import contentpage_migrator
        query = dict(object_provides=IContentPage.__identifier__)
        self.stats[IContentPage.__identifier__] = {
            'old': len(self.catalog(query))}
        contentpage_migrator(self.portal)

    def migrate_textblock(self):
        from ftw.contentpage.interfaces import ITextBlock
        from ftw.simplelayout.migration.textblock_migration import textblock_migrator
        query = dict(object_provides=ITextBlock.__identifier__)
        brains = self.catalog(query)
        self.stats[ITextBlock.__identifier__] = {
            'old': len(brains)}
        textblock_migrator(self.portal)

    def migrate_imageblock(self):
        from plone.app.blob.interfaces import IATBlobImage
        from ftw.simplelayout.migration.imageblock_migration import imageblock_migrator
        query = dict(object_provides=IATBlobImage.__identifier__)
        brains = self.catalog(query)
        self.stats[IATBlobImage.__identifier__] = {
            'old': len(brains)}
        imageblock_migrator(self.portal)

    def link_integrity_check(self, enable=False):
        ptool = self.portal.portal_properties
        site_props = getattr(ptool, 'site_properties', None)

        if enable:
            site_props.manage_changeProperties(
                enable_link_integrity_checks=self.link_integrity_state)
        else:
            self.link_integrity_state = site_props.getProperty(
                'enable_link_integrity_checks',
                False)
            site_props.manage_changeProperties(
                enable_link_integrity_checks=False)

    def patch_notify_modified(self):
        """Patch notifyModified to prevent setModificationDate() on changes

        notifyModified lives in several places and is also used on folders
        when their content changes.
        So when we migrate Documents before Folders the folders
        ModifiedDate gets changed.
        """
        for klass in PATCH_NOTIFY:
            patch(klass, 'notifyModified', pass_fn)

    def reset_notify_modified(self):
        """reset notifyModified to old state"""
        for klass in PATCH_NOTIFY:
            undoPatch(klass, 'notifyModified')

    def store_block_marker_interface(self):
        for brain in self.catalog(object_provides=ISimpleLayoutBlock.__identifier__):
            block = brain.getObject()
            if ISlotA.providedBy(block):
                setattr(block, '_simplelayout_slot', 'A')
            elif ISlotB.providedBy(block):
                setattr(block, '_simplelayout_slot', 'B')
            elif ISlotC.providedBy(block):
                setattr(block, '_simplelayout_slot', 'C')
            elif ISlotD.providedBy(block):
                setattr(block, '_simplelayout_slot', 'D')
