from ftw.simplelayout.browser.provider import SimplelayoutRenderer
from ftw.simplelayout.interfaces import IPageConfiguration
from zope.publisher.browser import BrowserView
import json


class ReloadLayoutView(BrowserView):
    """Reloads a layout by name and index also performs some modifications"""

    def __init__(self, context, request):
        super(ReloadLayoutView, self).__init__(context, request)
        self.data = None

    def __call__(self):
        self.data = json.loads(self.request.get('data', '{}'))

        self.name = self.data['name']
        self.layoutindex = int(self.data['layoutindex'])
        self.klasses = self.data['cssklasses']
        self.set_layout_state()
        return self.render_new_layout()

    def set_layout_state(self):
        page_conf = IPageConfiguration(self.context)
        self.new_state = page_conf.load()
        self.new_state.get(
            self.name)[self.layoutindex]['cssklasses'] = self.klasses
        page_conf.store(self.new_state)

    def render_new_layout(self):
        sl_renderer = SimplelayoutRenderer(self.context,
                                           self.new_state,
                                           self.name)
        return sl_renderer.render_layout(index=self.layoutindex)
