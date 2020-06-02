from ftw.referencewidget.sources import ReferenceObjSourceBinder
from ftw.referencewidget.widget import ReferenceBrowserWidget
from ftw.simplelayout import _
from ftw.simplelayout.aliasblock.contents.interfaces import IAliasBlock
from plone import api
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Item
from plone.directives import form
from plone.directives.form import widget
from z3c.relationfield.schema import RelationChoice
from zope.interface import alsoProvides
from zope.interface import implements


def get_selectable_blocks():
    return ['ftw.simplelayout.TextBlock',
            'ftw.simplelayout.GalleryBlock',
            'ftw.simplelayout.FileListingBlock',
            'ftw.sliderblock.SliderBlock',
            'ftw.news.NewsListingBlock',
            'ftw.events.EventListingBlock',
            'ftw.iframeblock.IFrameBlock',
            'ftw.addressblock.AddressBlock',
            'ftw.simplelayout.MapBlock']


class IAliasBlockSchema(form.Schema):
    """AliasBlock for simplelayout
    """

    widget('alias', ReferenceBrowserWidget,
           start='parent',
           )
    alias = RelationChoice(
        title=_(u'label_alias_content',
                default=u'Alias Content'),
        description=_(
            u'label_alias_description',
            default=u'Choose a block to be rendered within this block.'),
        required=True,
        source=ReferenceObjSourceBinder(
            selectable=get_selectable_blocks(),
            override=True
        )
    )


alsoProvides(IAliasBlockSchema, IFormFieldProvider)


class AliasBlock(Item):
    implements(IAliasBlock)
