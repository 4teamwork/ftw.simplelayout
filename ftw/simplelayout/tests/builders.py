from ftw.builder.archetypes import ArchetypesBuilder
from ftw.builder import builder_registry


class PageBuilder(ArchetypesBuilder):
    portal_type = 'Page'

builder_registry.register('sl page', PageBuilder)


class ParagraphBuilder(ArchetypesBuilder):
    portal_type = 'paragraph'

builder_registry.register('sl paragraph', ParagraphBuilder)
