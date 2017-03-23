from ftw.simplelayout.interfaces import IContentPageShowTitle
from ftw.simplelayout.interfaces import IPageConfiguration
from ftw.simplelayout.interfaces import ISimplelayoutView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zExceptions import BadRequest
from zope.interface import implements
from zope.publisher.browser import BrowserView
import json
import logging

LOG = logging.getLogger('ftw.simplelayout')


class SimplelayoutView(BrowserView):
    implements(ISimplelayoutView)

    template = ViewPageTemplateFile('templates/simplelayout.pt')

    def __call__(self):
        return self.template()

    def save_state(self):
        data = self.request.form.get('data')
        if data:
            json_conf = json.loads(data)
            page_conf = IPageConfiguration(self.context)
            page_conf.store(json_conf)
        else:
            raise BadRequest('No data given.')

        self.request.response.setHeader("Content-type", "application/json")
        return ''

    def update_simplelayout_settings(self, settings):
        pass

    def show_title(self):
        try:
            adapted_obj = IContentPageShowTitle(self.context)
            return adapted_obj.show_title
        except TypeError:
            return True
