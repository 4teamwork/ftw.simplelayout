from plone.app.layout.viewlets.common import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class OpenlayersViewlet(ViewletBase):
    index = ViewPageTemplateFile('openlayers.pt')
