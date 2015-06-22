from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.migration.testing import FTW_SIMPLELAYOUT_MIGRATON_TESTING
from plone.app.uuid.utils import uuidToObject
from plone.uuid.interfaces import IUUID
from unittest2 import TestCase


class TestImageBlockMigration(TestCase):

    layer = FTW_SIMPLELAYOUT_MIGRATON_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

        self.migration = self.portal.restrictedTraverse(
            '@@migrate_ftw_contentpage_to_ftw_simplelayout')

        self.contentpage = create(Builder('content page'))
        self.contentpage_uuid = IUUID(self.contentpage)

        self.imageblock = create(Builder('image')
                                 .within(self.contentpage)
                                 .with_dummy_content())
        self.imageblock.processForm()

        self.imageblock_uuid = IUUID(self.imageblock)

    def test_images_are_migrated_as_textblock_with_an_image_only(self):

        self.migration()

        new_image = uuidToObject(self.imageblock_uuid)

        self.assertEquals('ftw.simplelayout.TextBlock', new_image.portal_type)
        self.assertEquals(self.imageblock.getImage().data,
                          new_image.image.data)
        self.assertEquals(self.imageblock.Title(), new_image.Title())

    def test_images_not_in_simplelayout_page_are_not_treated_as_block(self):
        folder = create(Builder('folder'))
        image = create(Builder('image')
                       .within(folder)
                       .with_dummy_content())
        image_uuid = IUUID(image)

        self.migration()
        self.assertEquals(image, uuidToObject(image_uuid))
