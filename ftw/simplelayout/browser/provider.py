from Acquisition import aq_inner
from ftw.simplelayout.interfaces import IBlockProperties
from ftw.simplelayout.interfaces import IPageConfiguration
from ftw.simplelayout.interfaces import ISimplelayoutContainerConfig
from ftw.simplelayout.interfaces import ISimplelayoutDefaultSettings
from ftw.simplelayout.utils import normalize_portal_type
from plone import api
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ZODB.POSException import ConflictError
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.contentprovider.interfaces import ITALESProviderExpression
from zope.interface import implements
from zope.tales import expressions
import json
import logging


LOG = logging.getLogger('ftw.simplelayout')


class TalesSimplelayoutExpression(expressions.StringExpr):
    """Simplelayout tales expression
    Usage: <div tal:content='structure simplelayout: default' /> """

    implements(ITALESProviderExpression)

    fallbackview = ViewPageTemplateFile('templates/render_block_error.pt')
    structure = ViewPageTemplateFile('templates/structure.pt')

    def __call__(self, econtext):
        self.name = super(TalesSimplelayoutExpression, self).__call__(econtext)
        self.context = econtext.vars['context']
        self.request = econtext.vars['request']
        self.view = econtext.vars['view']

        return self.structure()

    def rows(self):
        """ Return datastructure for rendering blocks.
        """
        page_conf = IPageConfiguration(self.context)
        blocks = self._blocks()

        rows = page_conf.load().get(self.name, [])

        for row in rows:
            row['class'] = 'sl-layout'
            for col in row['cols']:
                col['class'] = 'sl-column sl-col-{}'.format(len(row['cols']))
                for block in col['blocks']:
                    if block['uid'] in blocks:
                        obj = blocks[block['uid']]
                        block['obj_html'] = self._render_block_html(obj)
                        block['type'] = normalize_portal_type(obj.portal_type)

        # Append blocks, which are not in the simplelayout configuration into
        # the last column.

        if self.name == 'default':
            for uid, obj in self._blocks_without_state():
                rows[-1]['cols'][-1]['blocks'].append(
                    {
                        'uid': uid,
                        'obj_html': self._render_block_html(obj),
                        'type': normalize_portal_type(obj.portal_type)
                    }
                )

        return rows

    def _get_first_column_config(self):
        settings = self._get_sl_settings()
        if settings and settings.get('layout'):
            return self._get_sl_settings()['layout'][0]
        else:
            # One column by default.
            return 1

    def _render_block_html(self, block):
        properties = queryMultiAdapter((block, self.request),
                                       IBlockProperties)

        view_name = properties.get_current_view_name()
        view = block.restrictedTraverse(view_name)

        try:
            html = view()
        except ConflictError:
            raise
        except Exception, exc:
            html = self.fallbackview()
            LOG.error('Could not render block: {}: {}'.format(
                exc.__class__.__name__,
                str(exc)))

        return html

    def _blocks(self):
        """ Return block objects by UID.
        """

        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        blocks = catalog(
            object_provides="ftw.simplelayout.interfaces.ISimplelayoutBlock",
            path={'query': '/'.join(context.getPhysicalPath()), 'depth': 1},
        )
        return {block.UID: block.getObject() for block in blocks}

    def _blocks_without_state(self):
        page_conf = IPageConfiguration(self.context)
        saved_blocks = []

        for container in page_conf.load().values():
            for row in container:
                for col in row['cols']:
                    for block in col['blocks']:
                        saved_blocks.append(block['uid'])

        return filter(lambda x: x[0] not in saved_blocks, self._blocks().items())

    def _get_sl_settings(self):
        # 1. global settings
        registry = getUtility(IRegistry)
        settings = json.loads(
            registry.forInterface(ISimplelayoutDefaultSettings).slconfig)

        # 2. Update with Permission check
        self.update_permission_related_settings(settings)

        # 3. Update with ISimplelayoutContainerConfig adapter
        adapter = queryMultiAdapter((self.context, self.request),
                                    ISimplelayoutContainerConfig)
        if adapter is not None:
            adapter(settings)

        # 4. View level customizations
        self.view.update_simplelayout_settings(settings)
        return settings

    def get_simplelayout_settings(self):
        return json.dumps(self._get_sl_settings())

    def update_permission_related_settings(self, settings):
        settings['canChangeLayouts'] = api.user.has_permission(
            'ftw.simplelayout: Change Layouts',
            obj=self.context)
