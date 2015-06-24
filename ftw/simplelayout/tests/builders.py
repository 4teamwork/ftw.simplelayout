from ftw.builder import builder_registry
from ftw.builder.dexterity import DexterityBuilder


class ContenPageBuilder(DexterityBuilder):
    portal_type = 'ftw.simplelayout.ContentPage'

builder_registry.register('sl content page', ContenPageBuilder)


class TextBlockBuilder(DexterityBuilder):
    portal_type = 'ftw.simplelayout.TextBlock'

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
