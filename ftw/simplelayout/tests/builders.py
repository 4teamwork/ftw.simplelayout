from ftw.builder import builder_registry
from ftw.builder.dexterity import DexterityBuilder
from StringIO import StringIO


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


class FileBuilder(DexterityBuilder):
    portal_type = 'ftw.simplelayout.File'

    def attach_file_containing(self, content, name="test.txt"):
        data = StringIO(content)
        data.filename = name
        self.attach(data)
        return self

    def attach(self, file_):
        self.arguments['file'] = file_
        return self

    def with_dummy_content(self):
        self.attach_file_containing("Test data")
        return self

builder_registry.register('sl file', FileBuilder)
