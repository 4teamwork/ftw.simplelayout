from ftw.simplelayout.behaviors import ITeaser
from ftw.simplelayout.interfaces import IBlockConfiguration
from plone.app.contenttypes.migration.migration import ATCTFolderMigrator
from plone.app.contenttypes.migration.migration import DocumentMigrator
from plone.namedfile.file import NamedBlobImage
from Products.CMFPlone.utils import safe_unicode
from Products.contentmigration.basemigrator.walker import CatalogWalker


def migrate(portal, migrator):
    """return a CatalogWalker instance in order
    to have its output after migration"""
    walker = CatalogWalker(portal, migrator)()
    return walker


class FtwContenPageMigrator(ATCTFolderMigrator):

    src_portal_type = 'ContentPage'
    src_meta_type = 'ContentPage'
    dst_portal_type = 'ftw.simplelayout.ContentPage'
    dst_meta_type = None  # not used


def contentpage_migrator(portal):
    return migrate(portal, FtwContenPageMigrator)


class FtwTextBlockMigrator(DocumentMigrator):

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
        if old_image == '':
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

    def migrate_simplelayout_block_state(self):
        old_image_layout = self.old.__annotations__.get('imageLayout', 'small')
        config = IBlockConfiguration(self.new)
        configdata = config.load()

        if old_image_layout == 'small':
            configdata['scale'] = 'mini'
            configdata['imagefloat'] = 'left'

        if old_image_layout == 'middle':
            configdata['scale'] = 'preview'
            configdata['imagefloat'] = 'left'

        if old_image_layout in ['full', 'no-image']:
            configdata['scale'] = 'large'
            configdata['imagefloat'] = 'no-float'

        if old_image_layout == 'middle-right':
            configdata['scale'] = 'preview'
            configdata['imagefloat'] = 'right'

        if old_image_layout == 'small-right':
            configdata['scale'] = 'mini'
            configdata['imagefloat'] = 'right'

        config.store(configdata)





def textblock_migrator(portal):
    return migrate(portal, FtwTextBlockMigrator)
