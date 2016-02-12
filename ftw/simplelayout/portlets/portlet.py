from zope.interface import implements
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from ftw.simplelayout.interfaces import IPageConfiguration


class ISimplelayoutPortlet(IPortletDataProvider):
    """
    Marker Interface for the simplelayout portlet.
    """


class Assignment(base.Assignment):

    implements(ISimplelayoutPortlet)

    @property
    def title(self):
        return "Simplelayout Portlet"


class Renderer(base.Renderer):

    render = ViewPageTemplateFile('templates/portlet.pt')

    @property
    def available(self):
        if self.has_blocks():
            return True
        else:
            disabled = int(self.request.get('disable_border', 0)) == 1
            return api.user.has_permission('Modify portal content',
                                           obj=self.context) and not disabled

    def has_blocks(self):
        config = IPageConfiguration(self.context)
        data = config.load()

        if self.manager.__name__ == 'plone.rightcolumn':
            portlet_container = data.get('portletright', [])
        elif self.manager.__name__ == 'plone.leftcolumn':
            portlet_container = data.get('portletleft', [])

        for layout in portlet_container:
            for columns in layout.values():
                for column in columns:
                    if len(column['blocks']):
                        return True
                    else:
                        continue
        return False


class AddForm(base.NullAddForm):
    def create(self):
        return Assignment()
