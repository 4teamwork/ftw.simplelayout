from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.behaviors import ITeaser
from ftw.simplelayout.contents.interfaces import ITextBlock
from ftw.simplelayout.interfaces import IBlockConfiguration
from ftw.simplelayout.migration.testing import FTW_SIMPLELAYOUT_MIGRATON_TESTING
from path import Path
from plone.app.textfield.value import RichTextValue
from plone.app.uuid.utils import uuidToObject
from plone.uuid.interfaces import IUUID
from StringIO import StringIO
from unittest2 import TestCase


def asset(filename):
    path = Path(__file__).dirname().realpath().joinpath('assets', filename)
    return path


def asset_as_StringIO(filename):
    result = StringIO(asset(filename).bytes())
    result.filename = filename
    return result


class TestTextBlockMigration(TestCase):

    layer = FTW_SIMPLELAYOUT_MIGRATON_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.migration = self.portal.restrictedTraverse(
            '@@migrate_ftw_contentpage_to_ftw_simplelayout')

        self.contentpage = create(Builder('content page')
                                  .having(excludeFromNav=True))
        self.contentpage_uuid = IUUID(self.contentpage)

        self.textblock = create(Builder('text block')
                                .within(self.contentpage)
                                .having(title='TextBlock Title',
                                        showTitle=True,
                                        text='<p>Some Text</p>',
                                        image=asset_as_StringIO('ipu.png'),
                                        imageClickable=True,
                                        imageCaption='image caption',
                                        imageAltText='image alt text',
                                        teaserExternalUrl='http://example.com',
                                        teaserReference=self.contentpage
                                        ))
        self.textblock_uuid = IUUID(self.textblock)

    def modfiy_textblock(self, block=None, imagelayout=None, viewname=None):
        if block is None:
            block = self.textblock

        if imagelayout is not None:
            block.__annotations__['imageLayout'] = imagelayout

        if viewname is not None:
            block.__annotations__['viewname'] = viewname

    def test_textblock_migration_basic(self):
        self.migration()
        new = uuidToObject(self.textblock_uuid)

        self.assertTrue(ITextBlock.providedBy(new))
        self.assertEquals(self.textblock.Title(), new.Title())
        self.assertTrue(isinstance(new.text, RichTextValue))
        self.assertEquals(self.textblock.getText(), new.text.output)
        self.assertEquals(self.textblock.getImage().filename,
                          new.image.filename)
        self.assertEquals(len(self.textblock.getImage().data),
                          len(new.image.data))
        # TODO Test image caption and image alt text
        self.assertEquals(self.textblock.getTeaserExternalUrl(),
                          ITeaser(new).external_link)
        self.assertEquals(uuidToObject(self.contentpage_uuid),
                          ITeaser(new).internal_link.to_object)

    def test_old_textblock_is_not_in_catalog_after_migration(self):
        self.assertEquals(1,
                          len(self.portal.portal_catalog(
                              portal_type='TextBlock')))

        self.migration()

        self.assertEquals(0,
                          len(self.portal.portal_catalog(
                              portal_type='TextBlock')))

    def test_imagelayout_small_is_migrated_properly(self):
        self.modfiy_textblock(imagelayout='small')
        self.migration()

        new_block = uuidToObject(self.textblock_uuid)
        blockconfig = IBlockConfiguration(new_block).load()

        self.assertEquals('mini', blockconfig['scale'])
        self.assertEquals('left', blockconfig['imagefloat'])

    def test_imagelayout_middle_is_migrated_properly(self):
        self.modfiy_textblock(imagelayout='middle')
        self.migration()

        new_block = uuidToObject(self.textblock_uuid)
        blockconfig = IBlockConfiguration(new_block).load()

        self.assertEquals('preview', blockconfig['scale'])
        self.assertEquals('left', blockconfig['imagefloat'])

    def test_imagelayout_full_is_migrated_properly(self):
        self.modfiy_textblock(imagelayout='full')
        self.migration()

        new_block = uuidToObject(self.textblock_uuid)
        blockconfig = IBlockConfiguration(new_block).load()

        self.assertEquals('large', blockconfig['scale'])
        self.assertEquals('no-float', blockconfig['imagefloat'])

    # XXX Currently we don't have this option (no-image) in the new
    # simplelayout.
    def test_imagelayout_no_image_is_migrated_properly(self):
        self.modfiy_textblock(imagelayout='no-image')
        self.migration()

        new_block = uuidToObject(self.textblock_uuid)
        blockconfig = IBlockConfiguration(new_block).load()

        self.assertEquals('large', blockconfig['scale'])
        self.assertEquals('no-float', blockconfig['imagefloat'])

    def test_imagelayout_middle_right_is_migrated_properly(self):
        self.modfiy_textblock(imagelayout='middle-right')
        self.migration()

        new_block = uuidToObject(self.textblock_uuid)
        blockconfig = IBlockConfiguration(new_block).load()

        self.assertEquals('preview', blockconfig['scale'])
        self.assertEquals('right', blockconfig['imagefloat'])

    def test_imagelayout_small_right_is_migrated_properly(self):
        self.modfiy_textblock(imagelayout='small-right')
        self.migration()

        new_block = uuidToObject(self.textblock_uuid)
        blockconfig = IBlockConfiguration(new_block).load()

        self.assertEquals('mini', blockconfig['scale'])
        self.assertEquals('right', blockconfig['imagefloat'])
