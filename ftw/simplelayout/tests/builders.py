from ftw.builder import builder_registry
from ftw.builder.archetypes import ArchetypesBuilder
from ftw.builder.dexterity import DexterityBuilder


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
