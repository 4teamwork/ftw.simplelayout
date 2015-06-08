from ftw.simplelayout.behaviors import ITeaser
from ftw.simplelayout.interfaces import IBlockConfiguration
from ftw.simplelayout.interfaces import IPageConfiguration
from plone.app.contenttypes.migration.migration import ATCTFolderMigrator
from plone.app.contenttypes.migration.migration import DocumentMigrator
from plone.namedfile.file import NamedBlobImage
from plone.uuid.interfaces import IUUID
from Products.CMFPlone.utils import safe_unicode
from Products.contentmigration.basemigrator.walker import CatalogWalker
from simplelayout.base.interfaces import IAdditionalListingEnabled
from simplelayout.base.interfaces import ISimpleLayoutBlock
from simplelayout.base.interfaces import ISimplelayoutTwoColumnOneOnTopView
from simplelayout.base.interfaces import ISimplelayoutTwoColumnView
from simplelayout.base.interfaces import ISimplelayoutView


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

    def migrate_prepare_page_state(self):
        config = IPageConfiguration(self.new)
        page_config = config.load()

        if ISimplelayoutView.providedBy(self.old):
            # On container, one layout and one column
            # this happens in 99% of all pages
            page_config = {
                "default": [
                    {"cols": [
                        {"blocks": []}]
                     }]}
        elif ISimplelayoutTwoColumnView.providedBy(self.old):
            page_config = {
                "default": [
                    {"cols": [
                        {"blocks": []},
                        {"blocks": []}]
                     }]}
        elif ISimplelayoutTwoColumnOneOnTopView.providedBy(self.old):
            page_config = {
                "default": [
                    {"cols": [
                        {"blocks": []}]},
                    {"cols": [
                        {"blocks": []},
                        {"blocks": []}]
                     }]}

        if IAdditionalListingEnabled.providedBy(self.old):
            # This adds a new one column simplelayout container
            page_config['additional'] = [
                {"cols": [{"blocks": []}]}]

        config.store(page_config)


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

    def migrate_block_slot_column_position(self):
        page = self.new.aq_parent
        config = IPageConfiguration(page)
        page_config = config.load()
        if len(page_config['default']) == 1 and len(page_config['default'][0]['cols']) == 1:
            # Do nothing, the block order is already OK (positionInParent)
            pass
        elif len(page_config['default']) == 1 and len(page_config['default'][0]['cols']) == 2:
            # Two columns one container and on layout
            if getattr(self.old, '_simplelayout_slot') == 'A':
                page_config['default'][0]['cols'][0]['blocks'].append(
                    {'uid': IUUID(self.new)})

            elif getattr(self.old, '_simplelayout_slot') == 'B':
                page_config['default'][0]['cols'][1]['blocks'].append(
                    {'uid': IUUID(self.new)})
            else:
                pass

        elif len(page_config['default']) == 2:
            # Two layouts, one containter. Firs layout has one column and the
            # second layout has two columns

            if getattr(self.old, '_simplelayout_slot') == 'A':
                # First layout, column one (the only column)
                page_config['default'][0]['cols'][0]['blocks'].append(
                    {'uid': IUUID(self.new)})

            elif getattr(self.old, '_simplelayout_slot') == 'B':
                # Second layout, first column
                page_config['default'][1]['cols'][0]['blocks'].append(
                    {'uid': IUUID(self.new)})

            elif getattr(self.old, '_simplelayout_slot') == 'C':
                # Second layout, second column
                page_config['default'][1]['cols'][1]['blocks'].append(
                    {'uid': IUUID(self.new)})

            else:
                pass

        if len(page_config.keys()) == 2:
            # Assume there is one more container called additional
            if getattr(self.old, '_simplelayout_slot') == 'D':
                page_config['additional'][0]['cols'][0]['blocks'].append(
                    {'uid': IUUID(self.new)})

        config.store(page_config)

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
