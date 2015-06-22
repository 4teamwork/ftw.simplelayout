from ftw.simplelayout.behaviors import ITeaser
from ftw.simplelayout.migration.migration_helpers import BlockMixin
from ftw.simplelayout.migration.migration_helpers import migrate
from plone.app.contenttypes.migration.migration import DocumentMigrator
from plone.namedfile.file import NamedBlobImage
from Products.CMFPlone.utils import safe_unicode


class FtwTextBlockMigrator(DocumentMigrator, BlockMixin):

    src_portal_type = 'TextBlock'
    src_meta_type = 'TextBlock'
    dst_portal_type = 'ftw.simplelayout.TextBlock'
    dst_meta_type = None  # not used

    def beforeChange_teaser_reference(self):
        teaser_reference_uid = self.old.getRawTeaserReference()
        if teaser_reference_uid:
            setattr(self.old,
                    '_teaser_reference_uid',
                    teaser_reference_uid)

    def migrate_schema_fields(self):
        # Migrates the text field
        super(FtwTextBlockMigrator, self).migrate_schema_fields()

        self.new.show_title = self.old.getShowTitle()

        old_image = self.old.getField('image').get(self.old)
        if old_image.data == '':
            return
        filename = safe_unicode(old_image.filename)
        namedblobimage = NamedBlobImage(data=old_image.data,
                                        filename=filename)
        self.new.image = namedblobimage

    def migrate_teaser_fields(self):
        ITeaser(self.new).external_link = self.old.getTeaserExternalUrl()
        self.old.getTeaserExternalUrl()
        # Check restore_teaser_reference method in view.py for internal
        # references.
        if hasattr(self.old, '_teaser_reference_uid'):
            setattr(self.new,
                    '_teaser_reference_uid',
                    self.old._teaser_reference_uid)


def textblock_migrator(portal):
    return migrate(portal, FtwTextBlockMigrator)
