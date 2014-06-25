from ftw.simplelayout import _
from ftw.simplelayout.contents.interfaces import IListingBlock
from ftw.simplelayout.contents.interfaces import IListingBlockColumns
from ftw.table import helper
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Container
from plone.directives import form
from z3c.form.browser.orderedselect import OrderedSelectWidget
from zope import schema
from zope.component import adapts
from zope.interface import alsoProvides
from zope.interface import implements
from zope.interface import Interface
from zope.schema.interfaces import IContextSourceBinder
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
    implements(IListingBlockColumns)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def columns(self):
        columns = (
            {'column': 'getContentType',
             'column_title': _(u'column_type', default=u'Type'),
             'sort_index': 'getContentType',
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

            {'column': 'review_state',
             'column_title': _(u'review_state', default=u'Review State'),
             'transform': helper.translated_string(),
             },

            {'column': 'id',
             'column_title': _(u'ID', default=u'ID'),
             'sort_index': 'id',
             },
        )
        return columns

