from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.contents.interfaces import IContentPage
from ftw.simplelayout.migration.testing import FTW_SIMPLELAYOUT_MIGRATON_TESTING
from plone.app.uuid.utils import uuidToObject
from plone.uuid.interfaces import IUUID
from unittest2 import TestCase


class TestContentPageMigration(TestCase):

    layer = FTW_SIMPLELAYOUT_MIGRATON_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.migration = self.portal.restrictedTraverse(
            '@@migrate_ftw_contentpage_to_ftw_simplelayout')

        related_contentpage1 = create(Builder('content page'))
        related_contentpage2 = create(Builder('content page'))
        self.related_contentpage1_uuid = IUUID(related_contentpage1)
        self.related_contentpage2_uuid = IUUID(related_contentpage2)

        self.contentpage = create(Builder('content page')
                                  .having(excludeFromNav=True,
                                          relatedItems=[related_contentpage1,
                                                        related_contentpage2]))
        self.contentpage_uuid = IUUID(self.contentpage)

    def test_contentpage_migration_basic(self):
        self.migration()
        new = uuidToObject(self.contentpage_uuid)

        self.assertTrue(IContentPage.providedBy(new))
        self.assertEquals(self.contentpage.Title(), new.Title())
        self.assertEquals(self.contentpage.getExcludeFromNav(),
                          new.exclude_from_nav)

    def test_old_page_is_not_in_catalog_after_migration(self):
        self.assertEquals(3,
                          len(self.portal.portal_catalog(
                              portal_type='ContentPage')))

        self.migration()

        self.assertEquals(0,
                          len(self.portal.portal_catalog(
                              portal_type='ContentPage')))

    def test_old_relations_on_other_contentpages_are_migrated(self):
        self.migration()
        new = uuidToObject(self.contentpage_uuid)
        new_related1 = uuidToObject(self.related_contentpage1_uuid)
        new_related2 = uuidToObject(self.related_contentpage2_uuid)

        self.assertEquals(2, len(new.relatedItems))
        # Also checks for the right order
        self.assertEquals([new_related1, new_related2],
                          [item.to_object for item in new.relatedItems])
