from collections import OrderedDict
from ftw.simplelayout import _
from ftw.simplelayout.browser.actions import DefaultActions
from ftw.simplelayout.contenttypes.contents import interfaces
from ftw.table import helper
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Container
from plone.directives import form
from zope import schema
from zope.component import adapts
from zope.component import queryMultiAdapter
from zope.i18n import translate
from zope.interface import alsoProvides
from zope.interface import directlyProvides
from zope.interface import implements
from zope.interface import Interface
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


def download_link(icon=True, classes=None, attrs=None, icon_only=False):

    def _helper(item, value):
        url = '%s/download' % item.getURL()
        attrs = {}
        attrs['href'] = url
        attrs['title'] = item.Description
        return helper.linked(item, value, show_icon=icon,
                             attrs=attrs, icon_only=icon_only)
    return _helper


class ListingBlockDefaultColumns(object):
    adapts(Interface, Interface)
    implements(interfaces.IListingBlockColumns)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def columns(self):
        columns = (
            {'column': 'getContentType',
             'column_title': _(u'column_type', default=u'Type'),
             'sort_index': 'portal_type',
             'transform': download_link(icon=True, icon_only=True)},

            {'column': 'Title',
             'column_title': _(u'column_title', default=u'Title'),
             'sort_index': 'sortable_title',
             'transform': download_link(icon=False)},

            {'column': 'modified',
             'column_title': _(u'column_modified', default=u'modified'),
             'sort_index': 'modified',
             'transform': helper.readable_date,
             },

            {'column': 'Creator',
             'column_title': _(u'column_creater', default=u'creater'),
             'transform': helper.readable_author,
             },

            {'column': 'getObjSize',
             'column_title': _(u'column_size', default=u'size'),
             },

            {'column': 'id',
             'column_title': _(u'ID', default=u'ID'),
             'sort_index': 'id',
             },
        )
        return columns


def listing_block_columns(context):
    terms = []
    adapter = queryMultiAdapter((context, context.REQUEST),
                                interfaces.IListingBlockColumns)

    for column in adapter.columns():
        terms.append(
            SimpleVocabulary.createTerm(
                column['column'],
                column['column'],
                column['column_title']))

    return SimpleVocabulary(terms)

directlyProvides(listing_block_columns, IContextSourceBinder)


def sort_index_vocabulary(context):
    adapter = queryMultiAdapter((context, context.REQUEST),
                                interfaces.IListingBlockColumns)
    terms = []
    for col in adapter.columns():
        if 'sort_index' in col:
            terms.append(SimpleVocabulary.createTerm(
                col['sort_index'],
                col['sort_index'],
                _(u'label_%s' % col['sort_index'],
                  default=col['sort_index'])))
    terms.append(SimpleVocabulary.createTerm(
        'getObjPositionInParent',
        'getObjPositionInParent',
        _(u'label_position_in_folder',
          default=u'Position in Folder')))

    return SimpleVocabulary(terms)

directlyProvides(sort_index_vocabulary, IContextSourceBinder)


sort_order_vocabulary = SimpleVocabulary([
    SimpleTerm(value='ascending',
               title=_(u'label_ascending', default=u'Ascending')),
    SimpleTerm(value='descending',
               title=_(u'label_descending', default=u'Descending'))
])


class IFileListingBlockSchema(form.Schema):
    """ListingBlock for simplelayout
    """

    title = schema.TextLine(
        title=_(u'label_title', default=u'Title'),
        required=False)

    show_title = schema.Bool(
        title=_(u'label_show_title', default=u'Show title'),
        default=True,
        required=False)

    columns = schema.List(
        title=_(u'label_columns', default=u'Columns'),
        value_type=schema.Choice(source=listing_block_columns),
        required=True,
        default=['getContentType', 'Title', 'modified'])

    sort_on = schema.Choice(
        title=_(u'label_sort_on', default=u'Sort by'),
        required=True,
        default="sortable_title",
        source=sort_index_vocabulary)

    sort_order = schema.Choice(
        title=_(u'label_sort_order', default=u'Sort order'),
        required=True,
        default="ascending",
        vocabulary=sort_order_vocabulary)


alsoProvides(IFileListingBlockSchema, IFormFieldProvider)


class FileListingBlock(Container):
    implements(interfaces.IFileListingBlock)


class ListingBlockActions(DefaultActions):

    def specific_actions(self):
        return OrderedDict([
            ('upload', {
                'class': 'upload icon-image-upload',
                'title': translate(
                    _(u'label_upload', default=u'Upload'),
                    context=self.request),
                'href': './sl-ajax-upload-block-view'
            }),
            ('folderContents', {
                'class': 'icon-folder-contents redirect',
                'title': translate(
                    _(u'label_folder_contents_files',
                      default=u'Go to folder contents for managing files'),
                    context=self.request),
                'href': '/folder_contents'
            }),
        ])
