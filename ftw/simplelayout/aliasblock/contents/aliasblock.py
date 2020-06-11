from ftw.referencewidget.selectable import DefaultSelectable
from ftw.referencewidget.sources import ReferenceObjSourceBinder
from ftw.referencewidget.widget import ReferenceBrowserWidget
from ftw.simplelayout import _
from ftw.simplelayout.aliasblock.contents.interfaces import IAliasBlock
from plone import api
from plone.uuid.interfaces import IUUID
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Item
from plone.directives import form
from plone.directives.form import widget
from z3c.form import validator
from z3c.relationfield.schema import RelationChoice
from zope.interface import alsoProvides
from zope.interface import implements
from zope.interface import Invalid


class AliasBlockSelectable(DefaultSelectable):

    def is_selectable(self):
        if not self.content:
            return False

        selectable = super(AliasBlockSelectable, self).is_selectable()
        is_sl_page = self.content.portal_type == 'ftw.simplelayout.ContentPage'

        # Don't allow sl pages containing another AliasBlock
        if is_sl_page:
            if IUUID(self.content) == IUUID(self.source.context):
                return False
            return not bool(filter(
                lambda item: item.portal_type == 'ftw.simplelayout.AliasBlock',
                self.content.objectValues()
            ))
        return selectable


def get_selectable_blocks():
    return ['ftw.simplelayout.TextBlock',
            'ftw.simplelayout.GalleryBlock',
            'ftw.simplelayout.FileListingBlock',
            'ftw.sliderblock.SliderBlock',
            'ftw.news.NewsListingBlock',
            'ftw.events.EventListingBlock',
            'ftw.iframeblock.IFrameBlock',
            'ftw.addressblock.AddressBlock',
            'ftw.simplelayout.MapBlock',
            'ftw.simplelayout.ContentPage']


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
            selectable_class=AliasBlockSelectable,
            selectable=get_selectable_blocks(),
            override=True
        )
    )


class ContentPageValidator(validator.SimpleFieldValidator):
    """Don't allow sl pages containing another AliasBlock"""

    def validate(self, value):
        """Validate international phone number on input"""
        if not value:
            raise Invalid(
                _(u'error_text_required_aliasblock',
                  default=u'A input is required'))


        if not AliasBlockSelectable(self.field.source, value)():
            if value.portal_type == 'ftw.simplelayout.ContentPage':
                raise Invalid(
                    _(u'error_text_sl_page_aliasblock',
                      default=u'The selected ContentPage contains a Aliasblock or is the page you are creating the block on and thus cannot be selected'))
            else:
                raise Invalid(
                    _(u'error_text_alias_aliasblock',
                      default=u'The selected content cannot be selected'))


validator.WidgetValidatorDiscriminators(
    ContentPageValidator,
    field=IAliasBlockSchema['alias']
)

alsoProvides(IAliasBlockSchema, IFormFieldProvider)


class AliasBlock(Item):
    implements(IAliasBlock)
