from ftw.simplelayout.migration.migration_helpers import BlockMixin
from ftw.simplelayout.migration.migration_helpers import migrate_image_blocks
from plone.app.contenttypes.migration.migration import BlobImageMigrator


class ImageBlockMigrator(BlobImageMigrator, BlockMixin):

    dst_portal_type = 'ftw.simplelayout.TextBlock'
    dst_meta_type = None  # not used


def imageblock_migrator(portal):
    return migrate_image_blocks(portal, ImageBlockMigrator)
