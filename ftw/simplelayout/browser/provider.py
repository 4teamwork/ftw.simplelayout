from Acquisition import aq_base
from Acquisition import aq_inner
from ftw.simplelayout.contenttypes.behaviors import IHiddenBlock
from ftw.simplelayout.interfaces import IPageConfiguration
from ftw.simplelayout.interfaces import ISimplelayoutContainerConfig
from ftw.simplelayout.interfaces import ISimplelayoutDefaultSettings
from ftw.simplelayout.utils import get_block_html
from ftw.simplelayout.utils import normalize_portal_type
from persistent.mapping import PersistentMapping
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
import re


LOG = logging.getLogger('ftw.simplelayout')


class CleanedViewPageTemplateFile(ViewPageTemplateFile):
    """Remove spaces and newlines between tags - This allows us to use
    'empty' selector in css.
    """

    def _prepare_html(self, text):
        text, type_ = super(ViewPageTemplateFile, self)._prepare_html(text)
        return re.sub(">\s*<", "><", text), type_


class SimplelayoutRenderer(object):

    layout_template = CleanedViewPageTemplateFile('templates/layout.pt')
    slot_template = CleanedViewPageTemplateFile('templates/slot.pt')
    fallbackview = ViewPageTemplateFile('templates/render_block_error.pt')

    def __init__(self, context, storage, name, view=None):

        self.context = context
        self.request = self.context.REQUEST
        self.storage = storage
        self.name = name
        self.view = view

    def render_slot(self):
        return self.slot_template()

    def render_layout(self, index=None, is_update=False):

        self.rows = self.storage.get(self.name, self._one_layout_one_column())

        # If index is None, render all layouts.
        # If not render only a specific layout
        if index is not None:
            if index > len(self.rows) - 1:
                raise ValueError('Layout with index {} does not exists'.format(
                    index))
            else:
                self.rows = [self.rows[index]]

        blocks = self._blocks()
        user_can_edit = self._user_can_edit()

        for row in self.rows:
            config = row.get('config', PersistentMapping())
            if not isinstance(config, PersistentMapping):
                config = config
            else:
                config = config.data

            row['class'] = ' '.join(config.values())
            row['config_json'] = json.dumps(config)

            for col in row['cols']:
                col['class'] = 'sl-column sl-col-{}'.format(len(row['cols']))
                col['blocks'] = filter(
                    lambda block: block.get('uid', '') in blocks,
                    col['blocks'])

                for block in col['blocks']:
                    obj = blocks[block['uid']]
                    self._create_or_update_block(obj, block)

                # Remove hidden blocks for users not having the permission
                # to edit content.
                col['blocks'] = [
                    block for block in col['blocks']
                    if not block['is_hidden'] or block['is_hidden'] and user_can_edit
                ]

        if self.name == 'default':
            for uid, obj in self._blocks_without_state():
                block = self._create_or_update_block(obj, uid=uid)

                # Skip hidden blocks for users not having the permission
                # to edit content.
                if block['is_hidden'] and not user_can_edit:
                    continue

                self.rows[-1]['cols'][-1]['blocks'].append(block)

        return self.layout_template(is_update=is_update)

    def get_simplelayout_settings(self):
        return json.dumps(self._get_sl_settings())

    def get_css_class(self):
        css_classes = ['sl-simplelayout']
        if self._user_can_edit():
            css_classes.append("sl-can-edit")
        return " ".join(css_classes)

    def _user_can_edit(self):
        return api.user.has_permission(
            'Modify portal content',
            obj=self.context) and int(self.request.get('disable_border', 0)) == 0

    def _one_layout_one_column(self):
        return [{"cols": [{"blocks": []}]}]

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
                        if 'uid' in block:
                            saved_blocks.append(block['uid'])

        return filter(lambda x: x[0] not in saved_blocks,
                      self._blocks().items())

    def _create_or_update_block(self, obj, block_dict=None, uid=None):
        if not block_dict:
            block_dict = {}

        if uid:
            block_dict['uid'] = uid

        block_type = normalize_portal_type(obj.portal_type)

        css_classes = ['sl-block', block_type]

        block_is_hidden = False
        hidden_block_support = IHiddenBlock(obj, None)
        if hidden_block_support:
            block_is_hidden = hidden_block_support.is_hidden
            if block_is_hidden:
                css_classes.append('hidden')

        css_classes.extend(getattr(aq_base(obj), 'additional_css_classes', []))

        block_dict['is_hidden'] = block_is_hidden
        block_dict['obj_html'] = self._render_block_html(obj)
        block_dict['type'] = block_type
        block_dict['url'] = obj.absolute_url()
        block_dict['id'] = obj.getId()
        block_dict['css_classes'] = ' '.join(css_classes)

        return block_dict

    def _get_sl_settings(self):
        # 1. global settings
        registry = getUtility(IRegistry)
        settings = json.loads(
            registry.forInterface(ISimplelayoutDefaultSettings,
                                  check=False).slconfig)

        # 2. Update with Permission check
        self._update_permission_related_settings(settings)

        # 3. Update with ISimplelayoutContainerConfig adapter
        adapter = queryMultiAdapter((self.context, self.request),
                                    ISimplelayoutContainerConfig)
        if adapter is not None:
            adapter(settings)

        # 4. View level customizations
        method = 'update_simplelayout_settings'
        if method in dir(self.view) and callable(getattr(self.view, method)):
            getattr(self.view, method)(settings)
        return settings

    def _render_block_html(self, block):

        try:
            html = get_block_html(block)
        except ConflictError:
            raise
        except Exception, exc:
            LOG.exception(exc)
            html = self.fallbackview()

        return html

    def _update_permission_related_settings(self, settings):
        settings['canChangeLayout'] = api.user.has_permission(
            'ftw.simplelayout: Change Layouts',
            obj=self.context)

        # Check if disable_border is in request, if it's there do not load
        # simplelayout.
        settings['canEdit'] = self._user_can_edit()


class BaseSimplelayoutExpression(object):

    def structure(self):
        """ Render a simplelayout slot by name.
        Name is given by the simplelayout expression.
        """
        page_conf = IPageConfiguration(self.context)
        storage = page_conf.load()
        sl_renderer = SimplelayoutRenderer(self.context,
                                           storage,
                                           self.name,
                                           view=self.view)

        return sl_renderer.render_slot()


class SimplelayoutExpression(BaseSimplelayoutExpression,
                             expressions.StringExpr):
    """Simplelayout tales expression
    Usage: <div tal:content='structure simplelayout: default' /> """

    implements(ITALESProviderExpression)

    def __call__(self, econtext):
        self.name = super(SimplelayoutExpression, self).__call__(econtext)
        self.context = econtext.vars['context']
        self.request = econtext.vars['request']
        self.view = econtext.vars['view']

        return self.structure()


try:
    from chameleon.astutil import Symbol
    from chameleon.tales import StringExpr
    from z3c.pt.expressions import ContextExpressionMixin
except ImportError:
    pass
else:
    def render_simplelayout_expression(econtext, name):
        renderer = BaseSimplelayoutExpression()
        renderer.name = name.strip()
        renderer.context = econtext.get('context')
        renderer.request = econtext.get('request')
        renderer.view = econtext.get('view')
        return renderer.structure()

    class ChameleonSimplelayoutExpression(ContextExpressionMixin, StringExpr):
        transform = Symbol(render_simplelayout_expression)
