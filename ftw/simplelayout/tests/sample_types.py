from collective import dexteritytextindexer
from ftw.builder import registry
from ftw.builder.dexterity import DexterityBuilder
from ftw.simplelayout.browser.blocks.base import BaseBlock
from ftw.simplelayout.interfaces import ISimplelayout
from ftw.simplelayout.interfaces import ISimplelayoutBlock
from plone.app.textfield import RichText
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Container
from plone.dexterity.content import Item
from plone.dexterity.fti import DexterityFTI
from plone.supermodel import model
from zope import schema
from zope.component import provideAdapter
from zope.interface import alsoProvides
from zope.interface import implements
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserView


# Schemas

class ISampleDXBlockSchema(model.Schema):
    title = schema.TextLine(
        title=u'Title',
        required=False)
    dexteritytextindexer.searchable('text')
    text = RichText(
        title=u'Text',
        required=False,
        allowed_mime_types=('text/html',))

alsoProvides(ISampleDXBlockSchema, IFormFieldProvider)


class ISampleSimplelayoutContainerSchema(model.Schema):
    pass


# Content types

class ISampleDXBlock(Interface):
    pass


class ISampleDXFolderishBlock(Interface):
    pass


class SampleBlock(Item):
    # In Plone 5 the ISimplelayoutBlock marker behavior does not work in tests.
    implements(ISampleDXBlock, ISimplelayoutBlock)


class SampleFolderishBlock(Container):
    implements(ISampleDXFolderishBlock, ISimplelayoutBlock)


class ISampleSimplelayoutContainer(Interface):
    pass


class SampleContainer(Container):
    # In Plone 5 the ISimplelayout marker behavior does not work in tests.
    implements(ISampleSimplelayoutContainer, ISimplelayout)


# Builders


class SampleContainerBuilder(DexterityBuilder):
    portal_type = 'SampleContainer'


class SampleBlockBuilder(DexterityBuilder):
    portal_type = 'SampleBlock'


class SampleFolderishBlockBuilder(DexterityBuilder):
    portal_type = 'SampleFolderishBlock'


registry.builder_registry.register('sample block', SampleBlockBuilder)
registry.builder_registry.register('sample container', SampleContainerBuilder)
registry.builder_registry.register('sample folderish block',
                                   SampleFolderishBlockBuilder)


# Setup

def setup_ftis(portal):

    types_tool = portal.portal_types

    # Simplelayout Container
    fti = DexterityFTI('SampleContainer')
    fti.schema = 'ftw.simplelayout.tests.sample_types.ISampleSimplelayoutContainerSchema'
    fti.klass = 'ftw.simplelayout.tests.sample_types.SampleContainer'
    fti.behaviors = (
        'ftw.simplelayout.interfaces.ISimplelayout',
        'plone.app.dexterity.behaviors.metadata.IBasic',
        'plone.app.content.interfaces.INameFromTitle',
        'collective.dexteritytextindexer.behavior.IDexterityTextIndexer')
    fti.default_view = '@@simplelayout-view'
    types_tool._setObject('SampleContainer', fti)

    # Simplelayout Block
    fti = DexterityFTI('SampleBlock')
    fti.schema = 'ftw.simplelayout.tests.sample_types.ISampleDXBlockSchema'
    fti.klass = 'ftw.simplelayout.tests.sample_types.SampleBlock'
    fti.default_view = 'block_view'
    fti.behaviors = (
        'ftw.simplelayout.interfaces.ISimplelayoutBlock',
        'plone.app.lockingbehavior.behaviors.ILocking',
        'plone.app.content.interfaces.INameFromTitle',)

    types_tool._setObject('SampleBlock', fti)

    # Simplelayout folderish Block
    fti = DexterityFTI('SampleFolderishBlock')
    fti.schema = 'ftw.simplelayout.tests.sample_types.ISampleDXBlockSchema'
    fti.klass = 'ftw.simplelayout.tests.sample_types.SampleFolderishBlock'
    fti.default_view = 'block_view'
    fti.global_allow = False
    fti.behaviors = (
        'ftw.simplelayout.interfaces.ISimplelayoutBlock',
        'plone.app.lockingbehavior.behaviors.ILocking',
        'plone.app.content.interfaces.INameFromTitle',)

    types_tool._setObject('SampleFolderishBlock', fti)
    folderishblock_fti = types_tool.get('SampleFolderishBlock')
    folderishblock_fti.allowed_content_types = ('SampleContainer', )

    contentpage_fti = types_tool.get('SampleContainer')
    contentpage_fti.allowed_content_types = ('SampleBlock', )


def setup_views():

    class SampleBlockView(BaseBlock):

        def __call__(self):
            return 'OK'

    provideAdapter(SampleBlockView,
                   adapts=(ISampleDXBlock, Interface),
                   provides=IBrowserView,
                   name='block_view')

    provideAdapter(SampleBlockView,
                   adapts=(ISampleDXFolderishBlock, Interface),
                   provides=IBrowserView,
                   name='block_view')

    class SampleBlockViewDifferent(BaseBlock):

        def __call__(self):
            return 'OK - different view'

    provideAdapter(SampleBlockViewDifferent,
                   adapts=(ISampleDXBlock, Interface),
                   provides=IBrowserView,
                   name='block_view_different')

    class SampleBlockViewBroken(BaseBlock):

        def __call__(self):
            raise

    provideAdapter(SampleBlockViewBroken,
                   adapts=(ISampleDXBlock, Interface),
                   provides=IBrowserView,
                   name='block_view_broken')
