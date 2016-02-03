from Acquisition._Acquisition import aq_inner
from ftw.simplelayout.browser.blocks.base import BaseBlock
from ftw.simplelayout.contenttypes.contents import interfaces
from ftw.table.interfaces import ITableGenerator
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import queryMultiAdapter
from zope.component import queryUtility


class FileListingBlockView(BaseBlock):
    """ListingBlock default view"""

    template = ViewPageTemplateFile('templates/listingblock.pt')

    def get_table_contents(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        return catalog(self._build_query)

    @property
    def _build_query(self):
        query = {}
        path = '/'.join(self.context.getPhysicalPath())
        query['path'] = {'query': path, 'depth': 1}
        query['sort_on'] = self.context.sort_on
        query['sort_order'] = self.context.sort_order
        return query

    def _get_columns(self, column_id):
        adapter = queryMultiAdapter((self.context, self.request),
                                    interfaces.IListingBlockColumns)
        for column in adapter.columns():
            if column_id == column['column']:
                return column
        return None

    def _filtered_columns(self):
        for column_id in self.context.columns:
            column = self._get_columns(column_id)
            if column:
                yield column

    def render_table(self):
        # Use a custom table template, because we don't want a table header id.
        # The id value is moved to a css klass.
        # Reason: It's no allowed to have an id more than once (In case we
        # have more than one Listingblock on one contentpage)
        template = ViewPageTemplateFile(
            'templates/ftw.table.custom.template.pt')
        generator = queryUtility(ITableGenerator, 'ftw.tablegenerator')
        return generator.generate(
            self.get_table_contents(),
            list(self._filtered_columns()),
            sortable=False,
            css_mapping={'table': 'listing nosort'},
            template=template,
            options={'table_summary': self.context.Title()},
            selected=(self._build_query['sort_on'],
                      self._build_query['sort_order']))

    @property
    def can_add(self):
        context = aq_inner(self.context)
        mtool = getToolByName(context, 'portal_membership')
        permission = mtool.checkPermission(
            'ftw.simplelayout: Add FileListingBlock', context)
        return bool(permission)
