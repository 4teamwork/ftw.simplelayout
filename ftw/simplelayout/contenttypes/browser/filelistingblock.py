from AccessControl.requestmethod import postonly
from Acquisition._Acquisition import aq_inner
from ftw.simplelayout.browser.blocks.base import BaseBlock
from ftw.simplelayout.contenttypes.behaviors import IMediaFolderReference
from ftw.simplelayout.contenttypes.behaviors import add_behavior_relations
from ftw.simplelayout.contenttypes.contents import interfaces
from ftw.simplelayout.staging.interfaces import IStaging
from ftw.table.interfaces import ITableGenerator
from plone import api
from plone.dexterity.utils import safe_utf8
from plone.protect import CheckAuthenticator
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.relationfield import RelationValue
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.i18n import translate
from zope.intid.interfaces import IIntIds


class FileListingBlockView(BaseBlock):
    """ListingBlock default view"""

    template = ViewPageTemplateFile('templates/listingblock.pt')
    table_template = ViewPageTemplateFile(
        'templates/ftw.table.custom.template.pt')

    def has_mediafolder(self):
        if not IMediaFolderReference(self.context, None):
            return False
        return self.context.mediafolder and self.context.mediafolder.to_object

    def can_access_media_folder(self):
        if not self.has_mediafolder():
            return False
        return api.user.has_permission('View', obj=self.context.mediafolder.to_object)

    def get_table_contents(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        return catalog(self._build_query)

    @property
    def _build_query(self):
        query = {}

        if self.has_mediafolder() and self.can_access_media_folder():
            path = '/'.join(self.context.mediafolder.to_object.getPhysicalPath())
        else:
            # Edge case for migrations/updates
            path = '/'.join(self.context.getPhysicalPath())

        query['path'] = {'query': path, 'depth': 1}
        query['sort_on'] = self.context.sort_on
        query['sort_order'] = safe_utf8(self.context.sort_order)
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
        generator = queryUtility(ITableGenerator, 'ftw.tablegenerator')
        return generator.generate(
            self.get_table_contents(),
            list(self._filtered_columns()),
            sortable=False,
            css_mapping={'table': 'listing nosort'},
            template=self.table_template,
            options={'table_summary': self.context.Title()},
            selected=(self._build_query['sort_on'],
                      self._build_query['sort_order']))

    @property
    def can_add(self):
        context = aq_inner(self.context)
        mtool = getToolByName(context, 'portal_membership')
        permission = mtool.checkPermission(
            'ftw.simplelayout: Add FileListingBlock', context)

        types_tool = api.portal.get_tool('portal_types')
        addable_content = types_tool['ftw.simplelayout.FileListingBlock'].allowed_content_types
        return bool(permission) and len(addable_content)

    def can_add_mediafolder(self):
        context = aq_inner(self.context).aq_parent

        if IStaging(context, None) and IStaging(context).is_working_copy():
            context = IStaging(context).get_baseline()

        mtool = getToolByName(context, 'portal_membership')
        permission = mtool.checkPermission(
            'ftw.simplelayout: Add ContentPage', context)
        return bool(permission)

    def get_review_state_mediafolder(self):
        if self.has_mediafolder():
            wftool = api.portal.get_tool('portal_workflow')
            state_id = wftool.getInfoFor(
                self.context.mediafolder.to_object,
                'review_state',
                default=None)
            if state_id is None:
                return ''
            translated_state_title = translate(state_id, context=self.request, domain='plone')
            return u'<span class="state-{}">{}</span>'.format(
                state_id,
                translated_state_title
            )
        return ''


class CreateAndLinkMediaFolder(BrowserView):

    @postonly
    def __call__(self, REQUEST):
        CheckAuthenticator(self.request)

        context = self.context.aq_parent

        if IStaging(context, None) and IStaging(context).is_working_copy():
            context = IStaging(context).get_baseline()

        mediafolder = api.content.create(
            type='ftw.simplelayout.MediaFolder',
            title=self.context.title_or_id(),
            container=context)

        intids = getUtility(IIntIds)
        relation = RelationValue(intids.getId(mediafolder))
        self.context.mediafolder = relation
        add_behavior_relations(self.context, None)

        url = mediafolder.absolute_url() + '/folder_contents'
        return self.request.RESPONSE.redirect(url)
