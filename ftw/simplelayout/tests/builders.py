from ftw.builder import builder_registry
from ftw.builder.dexterity import DexterityBuilder
from path import Path
from plone.namedfile.file import NamedBlobImage


class ContenPageBuilder(DexterityBuilder):
    portal_type = 'ftw.simplelayout.ContentPage'

builder_registry.register('sl content page', ContenPageBuilder)


class TextBlockBuilder(DexterityBuilder):
    portal_type = 'ftw.simplelayout.TextBlock'

    def with_dummy_image(self):
        image = Path(__file__).joinpath('..', 'assets', 'fullhd.jpg').abspath()
        self.arguments['image'] = NamedBlobImage(data=image.bytes(),
                                                 filename=u'test.gif')
        return self

builder_registry.register('sl textblock', TextBlockBuilder)


class ListingBlockBuilder(DexterityBuilder):
    portal_type = 'ftw.simplelayout.FileListingBlock'

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
