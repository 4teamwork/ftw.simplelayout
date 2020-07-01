from ftw.builder import builder_registry
from ftw.builder import create
from ftw.builder.dexterity import DexterityBuilder
from ftw.simplelayout.configuration import synchronize_page_config_with_blocks
from operator import methodcaller
from path import Path
from plone.namedfile.file import NamedBlobImage


class ContenPageBuilder(DexterityBuilder):
    portal_type = 'ftw.simplelayout.ContentPage'

    def __init__(self, session):
        super(ContenPageBuilder, self).__init__(session)
        self.block_builders = []

    def with_blocks(self, *block_builders):
        self.block_builders.extend(block_builders)
        return self

    def after_create(self, obj):
        if self.block_builders:
            map(create, map(methodcaller('within', obj), self.block_builders))
            synchronize_page_config_with_blocks(obj)
        return super(ContenPageBuilder, self).after_create(obj)

builder_registry.register('sl content page', ContenPageBuilder)


class TextBlockBuilder(DexterityBuilder):
    portal_type = 'ftw.simplelayout.TextBlock'

    def with_dummy_image(self):
        image = Path(__file__).joinpath('..', 'assets', 'fullhd.jpg').abspath()
        self.arguments['image'] = NamedBlobImage(data=image.bytes(),
                                                 filename=u'test.gif')
        return self

    def with_cropped_image(self):
        image = Path(__file__).joinpath('..', 'assets', 'cropped.jpg').abspath()
        self.arguments['cropped_image'] = NamedBlobImage(data=image.bytes(),
                                                         filename=u'cropped.gif')
        return self

builder_registry.register('sl textblock', TextBlockBuilder)


class ListingBlockBuilder(DexterityBuilder):
    portal_type = 'ftw.simplelayout.FileListingBlock'

    def __init__(self, session):
        super(ListingBlockBuilder, self).__init__(session)
        self.children_builders = []

    def with_files(self, *file_builders):
        self.children_builders.extend(file_builders)
        return self

    def after_create(self, obj):
        map(create, map(methodcaller('within', obj), self.children_builders))
        return super(ListingBlockBuilder, self).after_create(obj)

builder_registry.register('sl listingblock', ListingBlockBuilder)


class MapBlockBuilder(DexterityBuilder):
    portal_type = 'ftw.simplelayout.MapBlock'

builder_registry.register('sl mapblock', MapBlockBuilder)


class VideoBlockBuilder(DexterityBuilder):
    portal_type = 'ftw.simplelayout.VideoBlock'

builder_registry.register('sl videoblock', VideoBlockBuilder)


class GalleryBlockBuilder(DexterityBuilder):
    portal_type = 'ftw.simplelayout.GalleryBlock'

builder_registry.register('sl galleryblock', GalleryBlockBuilder)


class AliasBlockBuilder(DexterityBuilder):
    portal_type = 'ftw.simplelayout.AliasBlock'

builder_registry.register('sl aliasblock', AliasBlockBuilder)
