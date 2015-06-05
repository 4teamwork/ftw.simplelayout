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
from z3c.relationfield import RelationValue
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from ftw.simplelayout.behaviors import ITeaser


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
        # switch of setModificationDate on changes
        self.patch_notify_modified()
        # patch UUIDIndex - Prevent UUID Error-Messages when migrating folders.
        patch(
            UUIDIndex,
            'insertForwardIndexEntry',
            patched_insertForwardIndexEntry)

        # Migration
        self.migrate_contentpage()
        self.migrate_textblock()

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
        from ftw.simplelayout.migration.migration import contentpage_migrator
        query = dict(object_provides=IContentPage.__identifier__)
        self.stats[IContentPage.__identifier__] = {
            'old': len(self.catalog(query))}
        contentpage_migrator(self.portal)

    def migrate_textblock(self):
        from ftw.contentpage.interfaces import ITextBlock
        from ftw.simplelayout.migration.migration import textblock_migrator
        query = dict(object_provides=ITextBlock.__identifier__)
        self.stats[ITextBlock.__identifier__] = {
            'old': len(self.catalog(query))}
        textblock_migrator(self.portal)

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
