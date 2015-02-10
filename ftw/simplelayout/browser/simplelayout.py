from Acquisition import aq_inner
from ftw.simplelayout.interfaces import IBlockProperties
from ftw.simplelayout.interfaces import IPageConfiguration
from ftw.simplelayout.interfaces import ISimplelayoutView
from ftw.simplelayout.utils import normalize_portal_type
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ZODB.POSException import ConflictError
from zope.component import queryMultiAdapter
from zope.interface import implements
from zope.publisher.browser import BrowserView
import json
import logging


LOG = logging.getLogger('ftw.simplelayout')


class SimplelayoutView(BrowserView):
    implements(ISimplelayoutView)

    template = ViewPageTemplateFile('templates/simplelayout.pt')
    fallbackview = ViewPageTemplateFile('templates/render_block_error.pt')

    def __call__(self):
        return self.template()

    def rows(self):
        """ Return datastructure for rendering blocks.
        """
        page_conf = IPageConfiguration(self.context)
        blocks = self._blocks()

        rows = page_conf.load()
        for row in rows:
            row['class'] = 'sl-layout'
            for col in row['cols']:
                col['class'] = 'sl-column sl-col-{}'.format(len(row['cols']))
                for block in col['blocks']:
                    if block['uid'] in blocks:
                        obj = blocks[block['uid']]
                        block['obj_html'] = self._render_block_html(obj)
                        block['type'] = normalize_portal_type(obj.portal_type)
                        del blocks[block['uid']]

        # If we still have some blocks left make'em visible by adding them into
        # the last column.
        if blocks:
            # We need at least a column
            if not rows:
                rows = [{
                    'cols': [{
                        'blocks': [],
                        'class': 'sl-column sl-col-1',
                    }],
                    'class': 'sl-layout',
                }]

            for uid, obj in blocks.items():
                rows[-1]['cols'][-1]['blocks'].append(
                    {
                        'uid': uid,
                        'obj_html': self._render_block_html(obj),
                        'type': normalize_portal_type(obj.portal_type)
                    }
                )

        return rows

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

    def save_state(self):
        data = self.request.form.get('data')
        if data:
            json_conf = json.loads(data)
            page_conf = IPageConfiguration(self.context)
            page_conf.store(json_conf)

        self.request.response.setHeader("Content-type", "application/json")
        return ''
