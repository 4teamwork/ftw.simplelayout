from ftw.builder import builder_registry
from ftw.builder.archetypes import ArchetypesBuilder
from ftw.builder.dexterity import DexterityBuilder
from StringIO import StringIO


class PageBuilder(ArchetypesBuilder):
    portal_type = 'Page'

builder_registry.register('sl page', PageBuilder)


class ParagraphBuilder(ArchetypesBuilder):
    portal_type = 'paragraph'

builder_registry.register('sl paragraph', ParagraphBuilder)


class ContenPageBuilder(DexterityBuilder):
    portal_type = 'ftw.simplelayout.ContentPage'

builder_registry.register('sl content page', ContenPageBuilder)


class TextBlockBuilder(DexterityBuilder):
    portal_type = 'ftw.simplelayout.TextBlock'

builder_registry.register('sl textblock', TextBlockBuilder)


class ListingBlockBuilder(DexterityBuilder):
    portal_type = 'ftw.simplelayout.ListingBlock'

builder_registry.register('sl listingblock', ListingBlockBuilder)


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
